import pandas as pd

from src.transformations.country_groups import update_country_groups
from src.transformations.multi_selection_country_groups import process_multi_selection_country_groups

###########################
# Country groups
###########################

df = pd.read_csv(
    "../data/dataiku/raw/country_project/country_groups_new.csv",
    sep=",",
)
print(f"Size table before: {len(df)}")
country_groups = update_country_groups(df)
print(f"Size table before: {len(country_groups)}")
# check_df = country_groups[country_groups.country.isin(["Ecuador", "Qatar"])]
check_df = country_groups[country_groups.group_name.isin(["EU27"])]
print(check_df)
# country_groups.to_csv(
#     "../data/final/country_groups_prod.csv",
#     sep=",",
#     index=False,
# )

###########################
# Multi-selection groups
###########################

# df = pd.read_csv(
#     "../data/dataiku/raw/country_project/multiselect_groups.csv",
#     sep=",",
# )
# multi_selection_country_groups = process_multi_selection_country_groups(df)
# multi_selection_country_groups.to_csv(
#     "../data/final/multiselect_groups_prod.csv",
#     sep=",",
#     index=False,
# )
