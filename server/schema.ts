// This file is very very important, this is the heart of all the data types in both the client and the server.
// Each time you modify this file you'll have to re-generate the types with the appropriate command listed in the package.json file (normally it's "yarn generate").
// NB: You'll have to open a new terminal window to generate the types.
const { gql } = require("apollo-server-express");
export default gql`
  scalar JSON
  """
  All the energy units available.
  """
  enum EnergyUnit {
    Mtoe
    Mbtu
    Mb_per_d
    Mtce
    Tcf_gas
    Bcm
    TWh
    Gbl_per_yr
    TJ
    Mmbtu
    EJ
    toe
    KWh
  }

  """
  All the CO2 units available.
  """
  enum CO2Unit {
    GtCO2
    MtCO2
    KtCO2
    GtC
    MtC
    KtC
    tCO2
    KCO2
  }

  """
  All the CO2 equivalent units available.
  """
  enum CO2eqUnit {
    GtCO2eq
    MtCO2eq
    KtCO2eq
    GtCeq
    MtCeq
    KtCeq
    tCO2eq
  }

  type DimensionResult {
    categories: [String!]!
    series: [Serie]!
    multiSelects: [MultiSelect!]
  }

  type Serie {
    name: String!
    data: [Float]!
    color: String!
    dashStyle: DashStyle
    type: SerieType
  }
  # Comes from highcharts dashStyle
  enum DashStyle {
    Dash
    DashDot
    Dot
    LongDash
    LongDashDot
    LongDashDotDot
    ShortDash
    ShortDashDot
    ShortDashDotDot
    ShortDot
    Solid
  }
  # Comes from highcharts series type
  enum SerieType {
    spline
    line
  }
  type MultiSelect {
    name: String!
    data: [NameColor!]!
  }
  type NameColor {
    name: String!
    color: String!
  }

  """
  The World Energy History consumption and production
  """
  type PrimaryEnergies {
    "Markdown of the graph's description"
    mdInfos: String!
    "Units is all the units available for conversion"
    energyUnits: JSON
    "Sources is the names of the datasets sources"
    energyFamilies(type: String!): [NameColor!]!
    countries: [NameColor!]!
    "Groups is EU27, OECD..."
    groups: [NameColor!]!
    "Zones is basically continents"
    zones: [NameColor!]!
    "Multi-select presets"
    multiSelects(dimension: PrimaryEnergiesDimensions!, type: String!): [MultiSelect!]!
    "Types is Production or Consumption"
    types: [String!]!
    "Available dimensions e.g. by energy family, per capita, total"
    dimensions: [PrimaryEnergiesDimensions!]!
    "Share of primary energy by energy families"
    byEnergyFamily(
      energyFamilies: [String]!
      energyUnit: EnergyUnit!
      groupName: String
      type: String!
      yearStart: Int!
      yearEnd: Int!
    ): DimensionResult!
    "Total of all the energy families by countries, zones and groups."
    total(
      energyUnit: EnergyUnit!
      groupNames: [String]!
      type: String!
      yearStart: Int!
      yearEnd: Int!
    ): DimensionResult!
    "Per capita"
    perCapita(
      energyUnit: EnergyUnit!
      groupNames: [String]!
      yearStart: Int!
      yearEnd: Int!
      type: String!
    ): DimensionResult!
  }
  enum PrimaryEnergiesDimensions {
    total
    perCapita
    perGDP
    byEnergyFamily
  }
  """
  The World Final Energy History.
  """
  type FinalEnergies {
    "Markdown of the graph's description"
    mdInfos: String!
    "Units is all the units available for conversion"
    energyUnits: JSON
    energyFamilies: [NameColor!]!
    sectors: [NameColor!]!
    countries: [NameColor!]!
    "Groups is EU27, OECD..."
    groups: [NameColor!]!
    "Zones is basically continents"
    zones: [NameColor!]!
    "Multi-select presets"
    multiSelects(dimension: FinalEnergiesDimensions!): [MultiSelect!]!
    "Available dimensions e.g. by energy family, by sector, per capita, total"
    dimensions: [FinalEnergiesDimensions!]!
    "Share of primary energy by energy families"
    byEnergyFamily(
      energyFamilies: [String]
      energyUnit: EnergyUnit!
      groupName: String
      yearStart: Int!
      yearEnd: Int!
    ): DimensionResult!
    bySector(
      sectors: [String!]!
      energyUnit: EnergyUnit!
      groupName: String
      yearStart: Int!
      yearEnd: Int!
    ): DimensionResult!
    "Per capita"
    perCapita(energyUnit: EnergyUnit!, groupNames: [String]!, yearStart: Int!, yearEnd: Int!): DimensionResult!
    "Total of all the energy families by countries, zones and groups."
    total(energyUnit: EnergyUnit!, groupNames: [String]!, yearStart: Int!, yearEnd: Int!): DimensionResult!
  }
  enum FinalEnergiesDimensions {
    total
    perCapita
    byEnergyFamily
    bySector
    perGDP
  }

  type GHGByGas {
    "Markdown of the graph's description"
    mdInfos: String!
    "All the units available for conversion"
    emissionsUnits: JSON
    gases(source: String!): [NameColor!]!
    sectors(source: String!): [NameColor!]!
    "Sources is the names of the datasets sources"
    sources(dimension: GHGByGasDimensions!): [String!]!
    countries: [NameColor!]!
    "Groups is EU27, OECD..."
    groups: [NameColor!]!
    "GDP units"
    gdpUnits: [String!]!
    "Zones is basically continents"
    zones: [NameColor!]!
    multiSelects(dimension: GHGByGasDimensions!): [MultiSelect!]!
    "Available dimensions e.g. by gas, by sector, per capita, total"
    dimensions: [GHGByGasDimensions!]!
    "Share of emissions by gases"
    byGas(
      emissionsUnit: CO2eqUnit!
      gases: [String!]!
      groupName: String
      includingLUCF: Boolean!
      source: String!
      yearStart: Int!
      yearEnd: Int!
    ): DimensionResult!
    "Share of emissions by sector"
    bySector(
      source: String!
      sectors: [String!]!
      emissionsUnit: CO2eqUnit
      groupName: String
      yearStart: Int!
      yearEnd: Int!
    ): DimensionResult!
    perGDP(
      emissionsUnit: CO2Unit
      groupNames: [String]!
      gdpUnit: String!
      yearStart: Int!
      yearEnd: Int!
    ): DimensionResult!
    "Per capita. Multiple locations supported"
    perCapita(
      emissionsUnit: CO2eqUnit
      groupNames: [String]!
      yearStart: Int!
      yearEnd: Int!
      source: String!
    ): DimensionResult!
    "Total of all the Gases by countries, zones and groups. Multiple locations supported"
    total(
      source: String!
      emissionsUnit: CO2eqUnit
      groupNames: [String]!
      yearStart: Int!
      yearEnd: Int!
    ): DimensionResult!
  }

  enum GHGByGasDimensions {
    total
    perCapita
    byGas
    bySector
  }

  type Electricity {
    "Markdown of the graph's description"
    mdInfos: String!
    "Units is all the units available for conversion"
    energyUnits: JSON
    capacityEnergyFamilies: [NameColor!]!
    generationEnergyFamilies: [NameColor!]!
    countries: [NameColor!]!
    "Groups is EU27, OECD..."
    groups: [NameColor!]!
    "Zones is basically continents"
    zones: [NameColor!]!
    multiSelects(dimension: ElectricityDimensions!): [MultiSelect!]!
    "Available dimensions e.g. by energy family, per capita, total"
    dimensions: [ElectricityDimensions!]!
    "Types are Generation or Capacity"
    types: [String!]!
    "Total of all the energy families by countries, zones and groups."
    total(
      energyUnit: EnergyUnit
      groupNames: [String]!
      yearStart: Int!
      yearEnd: Int!
      type: ElectricityTypes!
    ): DimensionResult!
    "Share of primary energy by energy families"
    byEnergyFamily(
      capacityEnergyFamilies: [String]!
      generationEnergyFamilies: [String]!
      energyUnit: EnergyUnit
      groupName: String
      yearStart: Int!
      yearEnd: Int!
      type: ElectricityTypes!
    ): DimensionResult!
    "Per capita"
    perCapita(energyUnit: EnergyUnit, groupNames: [String]!, yearStart: Int!, yearEnd: Int!): DimensionResult!
  }
  enum ElectricityTypes {
    Generation
    Capacity
  }
  enum ElectricityDimensions {
    total
    perCapita
    byEnergyFamily
    perGDP
  }

  type CO2FromEnergy {
    "Markdown of the graph's description"
    mdInfos: String!
    "Units is all the units available for conversion"
    emissionsUnits: JSON
    "Sorted energy families by total of each one."
    energyFamilies: [NameColor!]!
    countries: [NameColor!]!
    "Groups is EU27, OECD..."
    groups: [NameColor!]!
    "Zones is basically continents"
    zones: [NameColor!]!
    multiSelects(dimension: CO2FromEnergyDimensions!): [MultiSelect!]!
    gdpUnits: [String!]!
    "Available dimensions e.g. by energy family, per capita, total, per GDP"
    dimensions: [CO2FromEnergyDimensions!]!
    "Total of all the energy families by countries, zones and groups."
    total(emissionsUnit: CO2Unit, groupNames: [String]!, yearStart: Int!, yearEnd: Int!): DimensionResult!
    perCapita(emissionsUnit: CO2Unit, groupNames: [String]!, yearStart: Int!, yearEnd: Int!): DimensionResult!
    perGDP(
      emissionsUnit: CO2Unit
      groupNames: [String]!
      gdpUnit: String!
      yearStart: Int!
      yearEnd: Int!
    ): DimensionResult!
    byEnergyFamily(
      emissionsUnit: CO2Unit
      energyFamilies: [String!]!
      groupName: String
      yearStart: Int!
      yearEnd: Int!
    ): DimensionResult!
  }
  enum CO2FromEnergyDimensions {
    total
    perCapita
    perGDP
    byEnergyFamily
  }

  type EnergyIntensityGDP {
    "Markdown of the graph's description"
    mdInfos: String!
    "Units is all the units available for conversion"
    energyUnits: JSON
    energyTypes: [String!]!
    countries: [NameColor!]!
    "Groups is EU27, OECD..."
    groups: [NameColor!]!
    "Zones is basically continents"
    zones: [NameColor!]!
    multiSelects: [MultiSelect!]!
    gdpUnits: [String!]!
    "Total of Primary Oil, Final Energy, Electricity or Primary Energy Consumption by different GDP units"
    total(
      energyUnit: EnergyUnit
      groupNames: [String]!
      energyType: String!
      gdpUnit: String!
      yearStart: Int!
      yearEnd: Int!
    ): DimensionResult!
  }
  enum EnergyIntensityGdpDimensions {
    total
  }
  type Oil {
    "Markdown of the graph's description"
    mdInfos: String!
    countries: [NameColor!]!
    "Groups is EU27, OECD..."
    groups: [NameColor!]!
    "Zones is basically continents"
    zones: [NameColor!]!
    multiSelects(countriesOnly: Boolean!): [MultiSelect!]!
    scenari: [NameColor!]!
    curves: [String!]!
    reserves: [String!]!
    oldScenari: [NameColor!]!
    oldCurves: [String!]!
    oldUrrs: [String!]!
    "Available dimensions e.g. by energy family, per capita, total"
    dimensions: [OilDimensions!]!
    "Units is all the units available for conversion"
    energyUnits: JSON
    "Sectors available"
    sectors: [NameColor!]!
    bySector(
      sectors: [String!]!
      energyUnit: EnergyUnit
      groupName: String
      yearStart: Int!
      yearEnd: Int!
    ): DimensionResult!
    perCapita(
      energyUnit: EnergyUnit
      groupNames: [String]!
      yearStart: Int!
      yearEnd: Int!
      type: String!
    ): DimensionResult!
    provenReserve(groupNames: [String]!, yearStart: Int!, yearEnd: Int!): DimensionResult!
    extrapolation(
      scenari: [String]!
      reserve: String!
      curves: [String]!
      yearStart: Int!
      yearEnd: Int!
    ): DimensionResult!
    oldExtrapolation(
      scenari: [String]!
      urr: String!
      curves: [String]!
      yearStart: Int!
      yearEnd: Int!
    ): DimensionResult!
    total(
      energyUnit: EnergyUnit
      groupNames: [String]!
      yearStart: Int!
      yearEnd: Int!
      type: String!
    ): DimensionResult!
  }
  enum OilDimensions {
    provenReserve
    extrapolation
    importExport
    total
    perCapita
    bySector
    perGDP
    oldExtrapolation
  }
  type Gas {
    "Markdown of the graph's description"
    mdInfos: String!
    countries: [NameColor!]!
    dimensions: [GasDimensions!]!
    "Groups is EU27, OECD..."
    groups: [NameColor!]!
    "Zones is basically continents"
    zones: [NameColor!]!
    multiSelects: [MultiSelect!]!
    "Units is all the units available for conversion"
    energyUnits: JSON
    "Sectors available"
    sectors: [NameColor!]!
    "Final consumption by sector"
    bySector(
      sectors: [String!]!
      energyUnit: EnergyUnit!
      groupName: String
      yearStart: Int!
      yearEnd: Int!
    ): DimensionResult!
    provenReserve(groupNames: [String]!, yearStart: Int!, yearEnd: Int!): DimensionResult!
    total(
      energyUnit: EnergyUnit
      groupNames: [String]!
      yearStart: Int!
      yearEnd: Int!
      type: String!
    ): DimensionResult!
    perCapita(energyUnit: EnergyUnit, groupNames: [String]!, yearStart: Int!, yearEnd: Int!): DimensionResult!
  }
  enum GasDimensions {
    provenReserve
    importExport
    total
    perCapita
    bySector
  }
  type Coal {
    "Markdown of the graph's description"
    mdInfos: String!
    countries: [NameColor!]!
    dimensions: [CoalDimensions!]!
    "Groups is EU27, OECD..."
    groups: [NameColor!]!
    "Zones is basically continents"
    zones: [NameColor!]!
    "Units is all the units available for conversion"
    multiSelects: [MultiSelect!]!
    energyUnits: JSON
    total(
      energyUnit: EnergyUnit
      groupNames: [String]!
      yearStart: Int!
      yearEnd: Int!
      type: String!
    ): DimensionResult!
    perCapita(
      energyUnit: EnergyUnit
      groupNames: [String]!
      yearStart: Int!
      yearEnd: Int!
      type: String!
    ): DimensionResult!
  }
  enum CoalDimensions {
    importExport
    total
    perCapita
  }

  type Footprint {
    "Markdown of the graph's description"
    mdInfos: String!
    "Units is all the units available for conversion"
    emissionsUnits: JSON
    countries: [NameColor!]!
    "Groups is EU27, OECD..."
    groups: [NameColor!]!
    "Zones is basically continents"
    zones: [NameColor!]!
    multiSelects(dimension: FootprintDimensions!): [MultiSelect!]!
    gdpUnits: [String!]!
    "Scopes will fetch 'Carbon Footprint' and 'Territorial Emissions'"
    scopes: [String!]!
    "Available dimensions e.g. by energy family, per capita, total, per GDP"
    dimensions: [FootprintDimensions!]!
    "Total of all the energy families by countries, zones and groups."
    total(
      emissionsUnit: CO2Unit
      groupNames: [String]!
      yearStart: Int!
      yearEnd: Int!
      scopes: [String]!
    ): DimensionResult!
    perCapita(
      emissionsUnit: CO2Unit
      groupNames: [String]!
      yearStart: Int!
      yearEnd: Int!
      scopes: [String]!
    ): DimensionResult!
    perGDP(
      emissionsUnit: CO2Unit
      groupNames: [String]!
      gdpUnit: String!
      yearStart: Int!
      yearEnd: Int!
      scopes: [String]!
    ): DimensionResult!
  }
  enum FootprintDimensions {
    total
    perCapita
    perGDP
  }

  type Kaya {
    "Markdown of the graph's description"
    mdInfos: String!
    countries: [NameColor!]!
    "Groups is EU27, OECD..."
    groups: [NameColor!]!
    "Zones is basically continents"
    zones: [NameColor!]!
    "Available dimensions e.g. by energy family, per capita, total, per GDP"
    dimensions: [KayaDimensions!]!
    "Total of all the energy families by countries, zones and groups."
    total(groupName: String): DimensionResult!
  }
  enum KayaDimensions {
    total
  }
  type Co2ImportsExports {
    "Markdown of the graph's description"
    mdInfos: String!
    multiSelects: [MultiSelect!]!
    countries(dimension: Co2ImportsExportsDimensions!): [NameColor!]!
    "Will return CO2 imports, exports and territorial emissions type name"
    types(dimension: Co2ImportsExportsDimensions!): [String!]!
    "Units is all the units available for conversion"
    emissionsUnits: JSON
    "Groups is EU27, OECD..."
    groups: [NameColor!]!
    "Zones is basically continents"
    zones: [NameColor!]!
    "Available dimensions e.g. by energy family, per capita, total, per GDP"
    dimensions: [Co2ImportsExportsDimensions!]!
    "Total imports and/or exports of CO2 per country"
    total(groupNames: [String]!, types: [String]!, emissionsUnit: CO2eqUnit): DimensionResult!
    "Get CO2 imports and exports by country from one country"
    byCountry(groupName: String, types: [String]!, numberOfCountries: Int!): DimensionResult!
    "Get CO2 imports and exports by continent from one country"
    byContinent(groupName: String, types: [String]!): DimensionResult!
    "Get CO2 imports and export by sector from one country"
    bySector(groupName: String, types: [String]!, numberOfSectors: Int!): DimensionResult!
  }
  enum Co2ImportsExportsDimensions {
    total
    byCountry
    byContinent
    bySector
  }

  type ImportExport {
    "Markdown of the graph's description"
    mdInfos: String!
    dimensions: [ImportExportDimensions!]!
    types: [String!]!
    total(
      groupNames: [String]!
      types: [String]!
      energyFamily: String!
      yearStart: Int!
      yearEnd: Int!
    ): DimensionResult!
  }
  enum ImportExportDimensions {
    total
  }
  type RenewableEnergies {
    "Markdown of the graph's description"
    mdInfos: String!
    "Units is all the units available for conversion"
    energyUnits: JSON
    countries: [NameColor!]!
    "Groups is EU27, OECD..."
    groups: [NameColor!]!
    "Zones is basically continents"
    zones: [NameColor!]!
    multiSelects(dimension: RenewableEnergiesDimensions!, type: String!): [MultiSelect!]!
    energyFamilies(type: String!): [NameColor!]!
    "Available dimensions e.g. by energy family, per capita, total, per GDP"
    dimensions: [RenewableEnergiesDimensions!]!
    "Types is Production or Consumption"
    types: [String!]!
    shareOfPrimaryEnergy(groupNames: [String]!, type: String!, yearStart: Int!, yearEnd: Int!): DimensionResult!
    "Share of primary energy by energy families"
    byEnergyFamily(
      energyFamilies: [String]!
      energyUnit: EnergyUnit!
      groupName: String
      type: String!
      yearStart: Int!
      yearEnd: Int!
    ): DimensionResult!
    "Total of all the energy families by countries, zones and groups."
    total(
      energyUnit: EnergyUnit!
      groupNames: [String]!
      type: String!
      yearStart: Int!
      yearEnd: Int!
    ): DimensionResult!
  }
  enum RenewableEnergiesDimensions {
    total
    shareOfPrimaryEnergy
    byEnergyFamily
  }
  type Nuclear {
    "Markdown of the graph's description"
    mdInfos: String!
    "Units is all the units available for conversion"
    energyUnits: JSON
    countries: [NameColor!]!
    "Groups is EU27, OECD..."
    groups: [NameColor!]!
    "Zones is basically continents"
    zones: [NameColor!]!
    multiSelects(dimension: NuclearDimensions!): [MultiSelect!]!
    "Available dimensions e.g. by energy family, per capita, total, per GDP"
    dimensions: [NuclearDimensions!]!
    shareOfElectricityGeneration(groupNames: [String]!, yearStart: Int!, yearEnd: Int!): DimensionResult!
    "Total of all the energy families by countries, zones and groups."
    total(energyUnit: EnergyUnit!, groupNames: [String]!, yearStart: Int!, yearEnd: Int!): DimensionResult!
  }
  enum NuclearDimensions {
    total
    shareOfElectricityGeneration
  }

  type Query {
    primaryEnergies: PrimaryEnergies
    finalEnergies: FinalEnergies
    gHGByGas: GHGByGas
    electricity: Electricity
    cO2FromEnergy: CO2FromEnergy
    energyIntensityGDP: EnergyIntensityGDP
    oil: Oil
    gas: Gas
    coal: Coal
    footprint: Footprint
    kaya: Kaya
    importExport: ImportExport
    renewableEnergies: RenewableEnergies
    nuclear: Nuclear
    co2ImportsExports: Co2ImportsExports
  }
`;
