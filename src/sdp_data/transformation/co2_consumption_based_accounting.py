import pandas as pd
from sdp_data.utils.translation import CountryTranslatorFrenchToEnglish
from sdp_data.utils.iso3166 import countries_by_alpha3


class EoraCbaPerZoneAndCountryProcessor:

    def __init__(self):
        self.dict_translation_record_code_to_scope = {
            "PBA_GgCO2PerBnUSDGDP": "Territorial Emissions per GDP",
            "CBA_GgCO2PerBnUSDGDP": "Carbon Footprint per GDP",
            "PBA_GgCO2": "Territorial Emissions",
            "CBA_GgCO2": "Carbon Footprint",
            "PBA_tCO2perCap": "Territorial Emissions per Capita",
            "CBA_tCO2perCap": "Carbon Footprint per Capita"
        }
        self.dict_translation_record_code_to_co2_unit = {
            "PBA_GgCO2PerBnUSDGDP": "MtCO2 per Trillion $ GDP",
            "CBA_GgCO2PerBnUSDGDP": "MtCO2 per Trillion $ GDP",
            "PBA_GgCO2": "MtCO2",
            "CBA_GgCO2": "MtCO2",
            "PBA_tCO2perCap": "tCO2 per capita",
            "CBA_tCO2perCap": "tCO2 per capita"
        }

    @staticmethod
    def unstack_years_in_dataframe(df: pd.DataFrame):
        df = df.unstack().reset_index()
        df.columns = ["country", "record_code", "co2"]
        return df

    @staticmethod
    def convert_giga_units(df_eora_cba):
        df_eora_cba.loc[df_eora_cba["record_code"].str.contains["Gg"], "co2"] /= 1000
        return df_eora_cba

    def compute_scope_from_record_code(self, df_eora_cba): # TODO - ajouter un test de raise Value error
        df_eora_cba["scope"] = df_eora_cba["record_code"].replace(self.dict_translation_record_code_to_scope)
        return df_eora_cba

    def compute_co2_unit_from_record_code(self, df_eora_cba):
        df_eora_cba["co2_unit"] = df_eora_cba["record_code"].replace(self.dict_translation_record_code_to_co2_unit)
        return df_eora_cba

    def run(self, df_eora_cba: pd.DataFrame, df_country: pd.DataFrame):
        """
        Computes the CO2 consumption stastistics per country and zone.
        :param df_eora_cba:
        :param df_country:
        :return:
        """
        # clean and filter countries
        df_eora_cba = df_eora_cba.rename({"Country": "country", "Record": "record_code"}, axis=1)
        df_eora_cba["country"] = CountryTranslatorFrenchToEnglish().run(df_eora_cba["Country"], raise_errors=False)
        df_eora_cba = df_eora_cba.dropna(subset=["country"], axis=1)
        df_eora_cba = self.convert_giga_units(df_eora_cba)

        # unstack the years.
        df_eora_cba = df_eora_cba.set_index(["country", "record_code"])
        df_eora_cba = self.unstack_years_in_dataframe(df_eora_cba)
        df_eora_cba["year"] = pd.to_numeric(df_eora_cba["year"])

        # create new columns scope, co2_unit and Source
        df_eora_cba["scope"] = self.compute_scope_from_record_code(df_eora_cba)
        df_eora_cba["scope"] = df_eora_cba["scope"].str.replace('Carbon Footprint', 'CO2 Footprint')
        df_eora_cba["co2_unit"] = self.compute_co2_unit_from_record_code(df_eora_cba)
        df_eora_cba["Source"] = "Eora"

        # join with countries
        df_eora_cba_per_zone = (pd.merge(df_country, df_eora_cba, on='country', how='left')
                                .groupby(['group_type', 'group_name', 'year', 'scope', 'co2_unit', 'source'])
                                .agg({'co2': "sum"})
                                .reset_index()
                                )

        # compute total co2 per country
        df_eora_cba_per_country = df_eora_cba.copy()
        df_eora_cba_per_country = df_eora_cba_per_country.rename({"country": "group_name"}, axis=1)
        df_eora_cba_per_country["group_type"] = "country"
        df_eora_cba_per_country = df_eora_cba_per_country[["group_type", "group_name", "year", "scope",
                                                           "co2", "co2_unit", "source"]]

        # concatenate countries and zones populations
        df_eora_cba_per_zone_and_countries = pd.concat([df_eora_cba_per_zone, df_eora_cba_per_country], axis=0)
        return df_eora_cba_per_zone_and_countries


class GcbPerZoneAndCountryProcessor:

    @staticmethod
    def unstack_years_in_dataframe(df: pd.DataFrame):
        df = df.unstack().reset_index()
        df.columns = ["country", "co2"]
        return df

    def run(self, df_gcb_territorial: pd.DataFrame, df_gcb_cba: pd.DataFrame, df_country: pd.DataFrame):

        # transpose and unstack years for the two datasets
        df_gcb_territorial = df_gcb_territorial.transpose()
        df_gcb_territorial = self.unstack_years_in_dataframe(df_gcb_territorial)
        df_gcb_cba = df_gcb_cba.transpose()
        df_gcb_cba = self.unstack_years_in_dataframe(df_gcb_cba)

        # concat the two dataframes and filter time and missing values
        df_gcb_territorial["scope"] = "Territorial Emissions"
        df_gcb_cba["scope"] = "Carbon Footprint"
        df_gcb = pd.concat([df_gcb_territorial, df_gcb_cba], axis=0)
        df_gcb["year"] = pd.to_numeric(df_gcb["year"])
        df_gcb = df_gcb[df_gcb["year"] >= 1990]
        df_gcb = df_gcb.dropna(subset=["co2"], axis=1)
        df_gcb["country"] = CountryTranslatorFrenchToEnglish().run(df_gcb["Country"], raise_errors=False)
        df_gcb = df_gcb.dropna(subset=["country"], axis=1)

        # create new columns scope, co2_unit and Source
        df_gcb["co2"] *= 3.664
        df_gcb["co2_unit"] = "MtCO2"
        df_gcb["Source"] = "Global Carbon Budget"
        df_gcb["scope"] = df_gcb["scope"].str.replace('Carbon Footprint', 'CO2 Footprint')

        # join with countries
        df_gcb_per_zone = (pd.merge(df_country, df_gcb, on='country', how='left')
                           .groupby(['group_type', 'group_name', 'year', 'scope', 'co2_unit', 'source'])
                           .agg({'co2': "sum"})
                           .reset_index()
                           )

        # compute total co2 per country
        df_gcb_per_country = df_gcb.copy()
        df_gcb_per_country = df_gcb_per_country.rename({"country": "group_name"}, axis=1)
        df_gcb_per_country["group_type"] = "country"
        df_gcb_per_country = df_gcb_per_country[["group_type", "group_name", "year", "scope",
                                                 "co2", "co2_unit", "source"]]

        # concatenate countries and zones populations
        df_gcb_per_zone_and_countries = pd.concat([df_gcb_per_zone, df_gcb_per_country], axis=0)
        return df_gcb_per_zone_and_countries



class EoraCo2TradePerZoneAndCountryProcessor:

    def __init__(self):
        self.countries_by_alpha3 = countries_by_alpha3

    def translate_country_code_to_country_name(self, serie_country_code_to_translate: pd.Series, raise_errors: bool):
        serie_country_translated = serie_country_code_to_translate.map(self.countries_by_alpha3)
        countries_no_translating = serie_country_translated[serie_country_translated.isnull()].values.tolist()
        print("WARN : no translating found for countries %s" % countries_no_translating)
        if raise_errors and serie_country_code_to_translate.isnll().sum() > 0:
            raise ValueError("ERROR : no translating found for countries %s" % countries_no_translating)

        return serie_country_translated

    @staticmethod
    def unstack_countries_in_dataframe(df: pd.DataFrame):
        df = df.unstack().reset_index()
        df.columns = ["country_to", "ghg", "country_from", "sector"]
        return df

    def run(self, df_eora_co2_trade: pd.DataFrame, df_country: pd.DataFrame):

        # translate the countries codes into countries names
        df_eora_co2_trade = df_eora_co2_trade.drop("ROW", axis=1)
        df_eora_co2_trade["country"] = self.translate_country_code_to_country_name(df_eora_co2_trade["country"], raise_errors=True)
        df_eora_co2_trade = df_eora_co2_trade.set_index(["country", "sector"])
        df_eora_co2_trade.columns = self.translate_country_code_to_country_name(df_eora_co2_trade.columns, raise_errors=True)

        # unstack the dataframe on countries
        df_eora_co2_trade = self.unstack_countries_in_dataframe(df_eora_co2_trade)
        df_eora_co2_trade["ghg_unit"] = "MtCO2e"
        df_eora_co2_trade = df_eora_co2_trade[['country_from', 'country_to', 'sector', 'ghg', 'ghg_unit']]

        # compute imports between countries
        df_exports = (df_eora_co2_trade
                      .groupby(['country_from', 'country_to', 'ghg_unit'])
                      .agg(co2=('ghg', 'sum')).reset_index()
                      )
        df_exports.loc[df_exports["country_from"] == df_exports["country_to"], "co2"] = 0.0
        df_exports = df_exports.rename({"country_from": "country", "ghg_unit": "co2_unit"})
        df_exports["type"] = "CO2 Exports"

        # compute exports between countries
        df_imports = (df_eora_co2_trade
                      .groupby(['country_to', 'country_from', 'ghg_unit'])
                      .agg(co2=('ghg', 'sum')).reset_index()
                      )
        df_imports.loc[df_exports["country_from"] == df_exports["country_to"], "co2"] = 0.0
        df_imports = df_exports.rename({"country_from": "country", "ghg_unit": "co2_unit"})
        df_exports["type"] = "CO2 Imports"

        df_trade_by_country = pd.concat([df_imports, df_exports], axis=0)

        # join and filter on the continent zones
        df_zones = df_country[df_country["group_type"] == "zone"]
        df_zones = df_zones[["country", "group_name"]]
        df_trade_by_country = df_trade_by_country.merge(df_zones, how="left", left_on="country_to", right_on="country")
        df_trade_by_country = df_trade_by_country.rename({"group_name": "continent_to"}, axis=1)
        list_continents = ["North America", "Central and South America", "Asia and Oceania", "Europe", "Africa"]
        df_trade_by_country = df_trade_by_country[df_trade_by_country["continent_to"].isin(list_continents)]


        return df_trade_by_country




class Co2ConsumptionBasedAccountingProcessor:

    def run(self, df_gcb_territorial: pd.DataFrame, df_gcb_cba: pd.DataFrame,
            df_eora_cba: pd.DataFrame, df_country: pd.DataFrame):

        # compute the EORA CBA per zones and countries
        list_scope_to_filter = ["Territorial Emissions", "CO2 Footprint"]
        df_eora_cba_per_zone_and_countries = EoraCbaPerZoneAndCountryProcessor().run(df_eora_cba, df_country)
        df_eora_cba_per_zone_and_countries = df_eora_cba_per_zone_and_countries[df_eora_cba_per_zone_and_countries.isin(list_scope_to_filter)]

        # compute the GCB per zones and countries
        df_gcb_per_zone_and_countries = GcbPerZoneAndCountryProcessor().run(df_gcb_territorial, df_gcb_cba, df_country)

        # stack the two datasets together
        df_footprint_vs_territorial = pd.concat([df_eora_cba_per_zone_and_countries, df_gcb_per_zone_and_countries], axis=0)

        return df_footprint_vs_territorial




