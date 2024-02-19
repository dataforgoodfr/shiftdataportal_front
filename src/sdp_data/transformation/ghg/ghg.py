import pandas as pd
from src.sdp_data.utils.translation import (
    CountryTranslatorFrenchToEnglish,
    SectorTranslator,
)
from src.sdp_data.utils.iso3166 import countries_by_name
from src.sdp_data.transformation.ghg.edgar import EdgarCleaner
from src.sdp_data.transformation.demographic.countries import (
    StatisticsPerCountriesAndZonesJoiner,
)
import numpy as np
from src.sdp_data.utils.format import StatisticsDataframeFormatter


class GhgPikEdgarCombinator:

    @staticmethod
    def compute_pik_edgar_stacked(df_pik_clean, df_edgar_clean):
        df_edgar_clean["source"] = "edgar"
        df_pik_edgar_stacked = pd.concat([df_pik_clean, df_edgar_clean], axis=0)
        df_pik_edgar_stacked = StatisticsDataframeFormatter().select_and_sort_values(df_pik_edgar_stacked, "ghg", round_statistics=4)
        return df_pik_edgar_stacked

    def compute_difference_pik_edgar_on_sector_industry(self, df_pik_clean, df_edgar_clean):
        """
        compute the difference between PIK and EDGAR on sector Industry and Construction
        :return:
        """
        df_edgar_industry = df_edgar_clean[df_edgar_clean["sector"] == "Industry and Construction"]
        df_pik_industry = df_pik_clean[df_pik_clean["sector"] == "Industry and Construction"]
        df_diff_industry = pd.merge(
            df_edgar_industry.drop("ghg_unit", axis=1),
            df_pik_industry,
            on=["country", "year", "gas", "sector"],
            suffixes=("_edgar", "_pik"),
        )
        df_diff_industry["ghg"] = (df_diff_industry["ghg_edgar"] - df_diff_industry["ghg_pik"])
        df_diff_industry = df_diff_industry[["country", "sector", "gas", "year", "ghg", "ghg_unit"]]
        return df_diff_industry

    def compute_pik_edgar_filter_sector(self, df_pik_clean, df_edgar_clean):
        """

        :param df_pik_clean:
        :param df_edgar_clean:
        :return:
        """
        df_pik_edgar_diff_industry = self.compute_difference_pik_edgar_on_sector_industry(df_pik_clean, df_edgar_clean)

        # concat with other EDGAR sectors
        df_edgar_filter_sector = df_edgar_clean[df_edgar_clean["sector"].isin(["Transport", "Electricity & Heat", "Other Energy"])]
        df_pik_edgar_sector = pd.concat([df_edgar_filter_sector, df_pik_edgar_diff_industry])
        df_pik_edgar_sector = StatisticsDataframeFormatter().select_and_sort_values(df_pik_edgar_sector, "ghg", round_statistics=4)
        return df_pik_edgar_sector

    @staticmethod
    def merge_edgar_pik_per_sector(df_pik_clean, df_edgar_clean, pik_sectors, edgar_sectors):
        df_pik_sector = df_pik_clean[(df_pik_clean["sector"].isin(pik_sectors)) & (df_pik_clean["ghg"] > 0)]
        df_edgar_sector = df_edgar_clean[df_edgar_clean["sector"].isin(edgar_sectors)]
        df_pik_edgar_merge_sector = df_pik_sector.merge(df_edgar_sector.drop(columns="ghg_unit"), how="inner", on=["country", "year", "gas"], suffixes=("_pik", "_edgar"))
        df_pik_edgar_merge_sector = df_pik_edgar_merge_sector.drop(columns=["source_pik", "source_edgar"])
        return df_pik_edgar_merge_sector

    def compute_pik_edgar_energy_ratio(self, df_pik_clean, df_edgar_clean):
        """

        """
        # Compute difference of GHG between Edgar Industry and PIK Industry
        df_edgar_industry = df_edgar_clean[df_edgar_clean["sector"] == "Industry and Construction"]
        df_pik_industry = df_pik_clean[(df_pik_clean["sector"] == "Industry and Construction")]
        df_pik_edgar_diff_industry = df_edgar_industry.merge(df_pik_industry, on=["country", "year", "gas"], suffixes=("_edgar", "_pik"))
        df_pik_edgar_diff_industry["ghg"] = df_pik_edgar_diff_industry["ghg_edgar"] - df_pik_edgar_diff_industry["ghg_pik"]
        df_pik_edgar_diff_industry["sector"] = "Energy from Industry"
        df_pik_edgar_diff_industry = df_pik_edgar_diff_industry.drop(columns=["ghg_unit_edgar", "ghg_unit_pik",
                                                                              "sector_pik", "sector_edgar",
                                                                              "ghg_pik", "ghg_edgar"])

        # concatenate with EDGAR and PIK transport and energy
        df_edgar_transport_energy = df_edgar_clean[df_edgar_clean["sector"].isin(["Transport", "Electricity & Heat", "Other Energy"])] 
        df_pik_edgar_diff_industry_transport = pd.concat([df_pik_edgar_diff_industry, df_edgar_transport_energy], axis=0)

        # merge on PIK energy
        df_pik_energy = df_pik_clean[(df_pik_clean["sector"] == "Energy") & (df_pik_clean["ghg"] > 0)]
        df_pik_energy_transport = df_pik_energy.merge(df_pik_edgar_diff_industry_transport.drop(columns="ghg_unit"),
                                                      how="inner", on=["country", "year", "gas"],
                                                      suffixes=("_pik", "_edgar"))
        df_pik_energy_transport = df_pik_energy_transport.drop(columns=["source_pik", "source_edgar"])

        # Filter and joint PIK and EDGAR on Agriculture, Waste and Industry
        df_pik_edgar_agriculture = self.merge_edgar_pik_per_sector(df_pik_clean, df_edgar_clean, ["Agriculture"], ["Agriculture", "Other Agriculture"])
        df_pik_edgar_waste = self.merge_edgar_pik_per_sector(df_pik_clean, df_edgar_clean, ['Waste', 'Other Sectors'], ['Waste', 'Other Sectors'])
        df_pik_edgar_industry = self.merge_edgar_pik_per_sector(df_pik_clean, df_edgar_clean, ['Industry and Construction'], ['Industry and Construction'])    # TODO -vérifier si erreur dans la requete SQL car dans dans la requete SQL originale, on fait ici le ratio PIK par PIK

        # join and compute ratio EDGAT - PIK
        df_pik_edgar_ratio = pd.concat([df_pik_energy_transport, df_pik_edgar_agriculture, df_pik_edgar_waste, df_pik_edgar_industry], axis=0)
        df_pik_edgar_ratio["ratio"] = df_pik_edgar_ratio["ghg_edgar"] / df_pik_edgar_ratio["ghg_pik"]

        return df_pik_edgar_ratio
    
    def compute_pik_edgar_extrapolated_glued(self, df_pik_clean, df_edgar_clean):  # TODO - revoir complètement cette méthode. Dette technique monstrueuse...
        # compute the energy ratio between PIK and Edgar
        print("\n----- Combine PIK and EDGAR extrapolated")
        df_pik_edgar_energy_ratio = self.compute_pik_edgar_energy_ratio(df_pik_clean, df_edgar_clean)
        df_pik_edgar_energy_ratio = df_pik_edgar_energy_ratio[(df_pik_edgar_energy_ratio["year"] >= 2008) & (df_pik_edgar_energy_ratio["year"] <= 2012)]
        df_pik_edgar_energy_ratio = df_pik_edgar_energy_ratio.groupby(["country", "gas", "sector_edgar", "sector_pik"]).agg(averaged_ratio=("ratio", "mean")).reset_index()

        # concatenate with the rest of PIK
        df_pik_clean = df_pik_clean.rename(columns={"ghg": "ghg_pik"})
        df_pik_edgar_energy_extrapolated = df_pik_edgar_energy_ratio.merge(df_pik_clean,
                                                                           how="inner",
                                                                           left_on=["country", "gas", "sector_pik"],
                                                                           right_on=["country", "gas", "sector"]
                                                                           )
        df_pik_edgar_energy_extrapolated["ghg_edgar_extrapolated"] = df_pik_edgar_energy_extrapolated["averaged_ratio"] * df_pik_edgar_energy_extrapolated["ghg_pik"]
        df_pik_edgar_energy_extrapolated["source"] = "pik_extrapolation"
        df_pik_edgar_energy_extrapolated = df_pik_edgar_energy_extrapolated.rename(columns={"sector_edgar": "sector"})

        # concatenate with PIK data greater than 2012
        df_pik_2012 = df_pik_clean[df_pik_clean["year"] > 2012]
        df_pik_edgar_extrapolated_computed = pd.concat([df_pik_edgar_energy_extrapolated, df_pik_2012])

        # Select columns from "GHG_EMISSIONS_edgar_cleaned2"
        df_edgar_clean = df_edgar_clean[["country", "sector", "gas", "year", "ghg", "ghg_unit"]]
        df_edgar_clean["source"] = "edgar"

        # Select columns from "GHG_EMISSIONS_pik_edgar_extrapolated"
        df_pik_edgar_extrapolated = df_pik_edgar_extrapolated_computed[["source", "country", "sector", "gas", "year", "ghg", "ghg_unit"]]
        df_pik_edgar_extrapolated["sector"] = np.where(df_pik_edgar_extrapolated["sector"] == "Energy from Industry", "Industry and Construction", df_pik_edgar_extrapolated["sector"])
        df_pik_edgar_extrapolated = df_pik_edgar_extrapolated[df_pik_edgar_extrapolated["sector"] != "Energy"]

        # Concatenate the two dataframes
        df_pik_edgar_extrapolated_glued = pd.concat([df_edgar_clean, df_pik_edgar_extrapolated], ignore_index=True)
        return df_pik_edgar_extrapolated_glued

    def run(self, df_edgar_clean, df_unfccc_annex_clean, df_pik_clean, df_country):
        """ """
        # merge PIK data and Edgar data
        df_pik_edgar_stacked = pd.concat([df_pik_unfccc, df_edgar_clean], axis=0)
        df_pik_edgar_merge = self.compute_pik_edgar(df_pik_clean, df_edgar_clean)

        # stack Unfccc and Edgar data and merge with countries
        df_pik_unfccc["source"] = "unfccc"
        df_edgar_clean["source"] = "edgar_cleaned2"
        df_pik_edgar_stacked = pd.concat([df_pik_unfccc, df_edgar_clean], axis=0)
        list_group_by = [
            "group_type",
            "group_name",
            "source",
            "year",
            "sector",
            "gas",
            "ghg_unit",
        ]
        dict_aggregation = {"ghg": "sum"}
        df_pik_edgar_stacked_per_zones_and_countries = (
            StatisticsPerCountriesAndZonesJoiner().run(
                df_pik_edgar_stacked, df_country, list_group_by, dict_aggregation
            )
        )


class PikUnfcccAnnexesCombinator:

     def run(self, df_pik_clean, df_unfccc_clean):
        print(df_pik_clean)
        print(df_pik_clean.columns)
        print(df_unfccc_clean)
        print(df_unfccc_clean.columns)
        df_pik_unfccc_annexes = pd.concat([df_pik_clean, df_unfccc_clean], axis=0)
        return StatisticsDataframeFormatter().select_and_sort_values(df_pik_unfccc_annexes, "ghg", round_statistics=4)



class EdgarUnfcccAnnexesCombinator:

    def run(self, df_edgar_clean, df_unfccc_annex_clean, df_country):
        # stack Unfccc and Edgar data
        df_unfccc_annex_clean["source"] = "unfccc"
        df_edgar_clean["source"] = "edgar"
        df_edgar_unfccc_stacked = pd.concat([df_edgar_clean, df_unfccc_annex_clean], axis=0)

        # merge with countries
        list_group_by = ["group_type", "group_name", "source", "year", "sector", "gas", "ghg_unit"]
        dict_aggregation = {"ghg": "sum"}
        df_edgar_unfccc_stacked_per_zones_and_countries = StatisticsPerCountriesAndZonesJoiner().run(df_edgar_unfccc_stacked, df_country, list_group_by, dict_aggregation)

        # aggregate per gas and per sector
        groupby_by_gas = ["source", "group_type", "group_name", "year", "gas"]
        df_ghg_edunf_by_gas = df_edgar_unfccc_stacked_per_zones_and_countries.groupby(groupby_by_gas).agg(ghg=("ghg", "sum"), ghg_unit=("ghg_unit", "first")).reset_index()
        df_ghg_edunf_by_gas = StatisticsDataframeFormatter().run(df_ghg_edunf_by_gas, "ghg", 5)

        groupby_by_sector = ["source", "group_type", "group_name", "year", "sector"]
        df_ghg_edunf_by_sector = df_edgar_unfccc_stacked_per_zones_and_countries.groupby(groupby_by_sector).agg(ghg=("ghg", "sum"), ghg_unit=("ghg_unit", "first")).reset_index()
        df_ghg_edunf_by_sector = StatisticsDataframeFormatter().run(df_ghg_edunf_by_sector, "ghg", 5)

        return df_ghg_edunf_by_gas, df_ghg_edunf_by_sector


class GhgMultiSourcesCombinator:

    def run(self, df_pik_clean, df_edgar_clean, df_fao_clean, df_country, df_cait_stacked):  # TODO - améliorer la jointures des données multi-sources ? données annexe plus utilisées depuis 2017
        """

        :param df_pik_clean:
        :param df_edgar_clean:
        :return:
        """
        # concatenate EDGAR and PIK
        df_edgar_clean["source"] = "EDGAR"
        df_edgar_sum = df_edgar_clean.groupby(["country", "year", "gas", "sector", "ghg_unit"]).agg(ghg=("ghg", "sum")).reset_index()
        df_multi_sources = pd.concat([df_pik_clean, df_edgar_sum], axis=0)

        # merge with countries and FAO
        df_multi_sources_per_country = df_country.merge(df_multi_sources, how="left", on="country")
        df_multi_sources_per_country = df_multi_sources_per_country[df_multi_sources_per_country["gas"].notnull()]
        list_group_by = ["sector", "gas", "year", "source", "group_name", "group_type"]
        df_multi_sources_sum_per_country = df_multi_sources_per_country.groupby(list_group_by).agg(ghg=("ghg", "sum"),
                                                                                                   ghg_unit=("ghg_unit", "first")).reset_index()
        df_multi_sources_sum_per_country["group_type"] = "country"
        df_multi_sources_sum_per_country["group_name"] = "country"
        df_ghg_multi_with_zones = pd.concat([df_multi_sources, df_multi_sources_sum_per_country, df_fao_clean], axis=0)
        
        # group by GAS and merge with CAIT        
        list_group_by_gas = ["sector", "group_type", "group_name", "year", "gas"]
        df_ghg_multi_by_gas = df_ghg_multi_with_zones.groupby(list_group_by_gas).agg(ghg=("ghg", "sum"), ghg_unit=("ghg_unit", "first")).reset_index()
        df_cait_stacked["source"] = "CAIT"
        df_ghg_multi_by_gas["including_lucf"] = np.nan
        df_cait_stacked = df_cait_stacked[(df_cait_stacked["gas"] != "") | (df_cait_stacked["gas"].notnull())]
        df_ghg_full_by_gas = pd.concat([df_ghg_multi_by_gas, df_cait_stacked], axis=0)
        df_ghg_full_by_gas = StatisticsDataframeFormatter().select_and_sort_values(df_ghg_full_by_gas, "ghg", 5)

        # group by SECTOR and merge with CAIT
        list_group_by_sector = ["sector", "group_type", "group_name", "year", "sector"]
        df_ghg_multi_by_sector = df_ghg_multi_with_zones.groupby(list_group_by_sector).agg(ghg=("ghg", "sum"), ghg_unit=("ghg_unit", "first")).reset_index()
        df_ghg_full_by_sector = pd.concat([df_ghg_multi_by_sector, df_cait_stacked.drop(columns="including_lucf")], axis=0)
        df_ghg_full_by_sector = StatisticsDataframeFormatter().select_and_sort_values(df_ghg_full_by_sector, "ghg", 5)

        # compute full aggregated
        list_group_by_all = ["sector", "group_type", "group_name", "year"]
        df_ghg_full_aggregated = df_ghg_multi_with_zones.groupby(list_group_by_all).agg(ghg=("ghg", "sum")).reset_index()
        df_ghg_full_aggregated = StatisticsDataframeFormatter().select_and_sort_values(df_ghg_full_aggregated, "ghg", 5)

        return df_ghg_full_by_gas, df_ghg_full_by_sector, df_ghg_full_aggregated
        



        

