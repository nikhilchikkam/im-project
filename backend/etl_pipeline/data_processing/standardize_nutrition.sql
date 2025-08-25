--- added sugars ------
with conversions as (
  select 'added_sugars' as nutrient_label, 'g' as standardized_unit, 'GRM' as unit, 1.0 as multiplier union
  select 'added_sugars', 'g', 'MGM', 0.001 union
  select 'added_sugars', 'g', 'MC', 0.000001 union
  select 'added_sugars', 'g', 'ONZ', 28.3495 union
  select 'added_sugars', 'g', 'GRN', 0.06479891
)
update product_nutrition pn
set 
  standardized_unit = c.standardized_unit,
  standardized_value = pn.value * c.multiplier
from conversions c
where lower(pn.nutrient_label) = lower(c.nutrient_label)
  and pn.unit = c.unit;

update product_nutrition
set standardized_unit = 'FLAGGED_UNIT',
    standardized_value = null
where nutrient_label = 'added_sugars'
  and standardized_unit is null;

--- Calcium --------
with conversions as (
  select 'calcium' as nutrient_label, 'mg' as standardized_unit, 'MGM' as unit, 1.0 as multiplier union
  select 'calcium', 'mg', 'GRM', 1000.0 union
  select 'calcium', 'mg', 'MC', 0.001 union
  select 'calcium', 'mg', 'ONZ', 28349.5 union
  select 'calcium', 'mg', 'GRN', 64.79891
)
update product_nutrition pn
set 
  standardized_unit = c.standardized_unit,
  standardized_value = pn.value * c.multiplier
from conversions c
where lower(pn.nutrient_label) = lower(c.nutrient_label)
  and pn.unit = c.unit;

update product_nutrition
set standardized_unit = 'FLAGGED_UNIT',
    standardized_value = null
where nutrient_label = 'calcium'
  and standardized_unit is null;

--- calories ------
with conversions as (
  select 'calories' as nutrient_label, 'kcal' as standardized_unit, 'E14' as unit, 1.0 as multiplier union  -- Kilocalorie
  select 'calories', 'kcal', 'D70', 1.0 union  -- Kilocalorie (same as E14)
  select 'calories', 'kcal', 'KJO', 0.239006 union  -- Kilojoule to Kilocalorie
  select 'calories', 'kcal', 'JOU', 0.000239006  -- Joule to Kilocalorie
)
update product_nutrition pn
set 
  standardized_unit = c.standardized_unit,
  standardized_value = pn.value * c.multiplier
from conversions c
where lower(pn.nutrient_label) = lower(c.nutrient_label)
  and pn.unit = c.unit;

update product_nutrition
set standardized_unit = 'FLAGGED_UNIT',
    standardized_value = null
where nutrient_label = 'calories'
  and standardized_unit is null;

--- cholesterol ------
with conversions as (
  select 'cholesterol' as nutrient_label, 'mg' as standardized_unit, 'MGM' as unit, 1.0 as multiplier union
  select 'cholesterol', 'mg', 'GRM', 1000.0 union
  select 'cholesterol', 'mg', 'MC', 0.001 union
  select 'cholesterol', 'mg', 'ONZ', 28349.5 union
  select 'cholesterol', 'mg', 'GRN', 64.79891
)
update product_nutrition pn
set 
  standardized_unit = c.standardized_unit,
  standardized_value = pn.value * c.multiplier
from conversions c
where lower(pn.nutrient_label) = lower(c.nutrient_label)
  and pn.unit = c.unit;

update product_nutrition
set standardized_unit = 'FLAGGED_UNIT',
    standardized_value = null
where nutrient_label = 'cholesterol'
  and standardized_unit is null;

--- dietary_fiber ------
with conversions as (
  select 'dietary_fiber' as nutrient_label, 'g' as standardized_unit, 'GRM' as unit, 1.0 as multiplier union
  select 'dietary_fiber', 'g', 'MGM', 0.001 union
  select 'dietary_fiber', 'g', 'MC', 0.000001 union
  select 'dietary_fiber', 'g', 'ONZ', 28.3495 union
  select 'dietary_fiber', 'g', 'GRN', 0.06479891
)
update product_nutrition pn
set 
  standardized_unit = c.standardized_unit,
  standardized_value = pn.value * c.multiplier
from conversions c
where lower(pn.nutrient_label) = lower(c.nutrient_label)
  and pn.unit = c.unit;

update product_nutrition
set standardized_unit = 'FLAGGED_UNIT',
    standardized_value = null
where nutrient_label = 'dietary_fiber'
  and standardized_unit is null;

--- iron ------
with conversions as (
  select 'iron' as nutrient_label, 'mg' as standardized_unit, 'MGM' as unit, 1.0 as multiplier union
  select 'iron', 'mg', 'GRM', 1000.0 union
  select 'iron', 'mg', 'MC', 0.001 union
  select 'iron', 'mg', 'ONZ', 28349.5 union
  select 'iron', 'mg', 'GRN', 64.79891
)
update product_nutrition pn
set 
  standardized_unit = c.standardized_unit,
  standardized_value = pn.value * c.multiplier
from conversions c
where lower(pn.nutrient_label) = lower(c.nutrient_label)
  and pn.unit = c.unit;

update product_nutrition
set standardized_unit = 'FLAGGED_UNIT',
    standardized_value = null
where nutrient_label = 'iron'
  and standardized_unit is null;

--- potassium ------
with conversions as (
  select 'potassium' as nutrient_label, 'mg' as standardized_unit, 'MGM' as unit, 1.0 as multiplier union
  select 'potassium', 'mg', 'GRM', 1000.0 union
  select 'potassium', 'mg', 'MC', 0.001 union
  select 'potassium', 'mg', 'ONZ', 28349.5 union
  select 'potassium', 'mg', 'GRN', 64.79891
)
update product_nutrition pn
set 
  standardized_unit = c.standardized_unit,
  standardized_value = pn.value * c.multiplier
from conversions c
where lower(pn.nutrient_label) = lower(c.nutrient_label)
  and pn.unit = c.unit;

update product_nutrition
set standardized_unit = 'FLAGGED_UNIT',
    standardized_value = null
where nutrient_label = 'potassium'
  and standardized_unit is null;

--- protein ------
with conversions as (
  select 'protein' as nutrient_label, 'g' as standardized_unit, 'GRM' as unit, 1.0 as multiplier union
  select 'protein', 'g', 'MGM', 0.001 union
  select 'protein', 'g', 'MC', 0.000001 union
  select 'protein', 'g', 'ONZ', 28.3495 union
  select 'protein', 'g', 'GRN', 0.06479891
)
update product_nutrition pn
set 
  standardized_unit = c.standardized_unit,
  standardized_value = pn.value * c.multiplier
from conversions c
where lower(pn.nutrient_label) = lower(c.nutrient_label)
  and pn.unit = c.unit;

update product_nutrition
set standardized_unit = 'FLAGGED_UNIT',
    standardized_value = null
where nutrient_label = 'protein'
  and standardized_unit is null;

--- saturated_fat ------
with conversions as (
  select 'saturated_fat' as nutrient_label, 'g' as standardized_unit, 'GRM' as unit, 1.0 as multiplier union
  select 'saturated_fat', 'g', 'MGM', 0.001 union
  select 'saturated_fat', 'g', 'MC', 0.000001 union
  select 'saturated_fat', 'g', 'ONZ', 28.3495 union
  select 'saturated_fat', 'g', 'GRN', 0.06479891
)
update product_nutrition pn
set 
  standardized_unit = c.standardized_unit,
  standardized_value = pn.value * c.multiplier
from conversions c
where lower(pn.nutrient_label) = lower(c.nutrient_label)
  and pn.unit = c.unit;

update product_nutrition
set standardized_unit = 'FLAGGED_UNIT',
    standardized_value = null
where nutrient_label = 'saturated_fat'
  and standardized_unit is null;

--- sodium ------
with conversions as (
  select 'sodium' as nutrient_label, 'mg' as standardized_unit, 'MGM' as unit, 1.0 as multiplier union
  select 'sodium', 'mg', 'GRM', 1000.0 union
  select 'sodium', 'mg', 'MC', 0.001 union
  select 'sodium', 'mg', 'ONZ', 28349.5 union
  select 'sodium', 'mg', 'GRN', 64.79891
)
update product_nutrition pn
set 
  standardized_unit = c.standardized_unit,
  standardized_value = pn.value * c.multiplier
from conversions c
where lower(pn.nutrient_label) = lower(c.nutrient_label)
  and pn.unit = c.unit;

update product_nutrition
set standardized_unit = 'FLAGGED_UNIT',
    standardized_value = null
where nutrient_label = 'sodium'
  and standardized_unit is null;

--- sugars ------
with conversions as (
  select 'sugars' as nutrient_label, 'g' as standardized_unit, 'GRM' as unit, 1.0 as multiplier union
  select 'sugars', 'g', 'MGM', 0.001 union
  select 'sugars', 'g', 'MC', 0.000001 union
  select 'sugars', 'g', 'ONZ', 28.3495 union
  select 'sugars', 'g', 'GRN', 0.06479891
)
update product_nutrition pn
set 
  standardized_unit = c.standardized_unit,
  standardized_value = pn.value * c.multiplier
from conversions c
where lower(pn.nutrient_label) = lower(c.nutrient_label)
  and pn.unit = c.unit;

update product_nutrition
set standardized_unit = 'FLAGGED_UNIT',
    standardized_value = null
where nutrient_label = 'sugars'
  and standardized_unit is null;

--- total_carbohydrate ------
with conversions as (
  select 'total_carbohydrate' as nutrient_label, 'g' as standardized_unit, 'GRM' as unit, 1.0 as multiplier union
  select 'total_carbohydrate', 'g', 'MGM', 0.001 union
  select 'total_carbohydrate', 'g', 'MC', 0.000001 union
  select 'total_carbohydrate', 'g', 'ONZ', 28.3495 union
  select 'total_carbohydrate', 'g', 'GRN', 0.06479891
)
update product_nutrition pn
set 
  standardized_unit = c.standardized_unit,
  standardized_value = pn.value * c.multiplier
from conversions c
where lower(pn.nutrient_label) = lower(c.nutrient_label)
  and pn.unit = c.unit;

update product_nutrition
set standardized_unit = 'FLAGGED_UNIT',
    standardized_value = null
where nutrient_label = 'total_carbohydrate'
  and standardized_unit is null;

--- total_fat ------
with conversions as (
  select 'total_fat' as nutrient_label, 'g' as standardized_unit, 'GRM' as unit, 1.0 as multiplier union
  select 'total_fat', 'g', 'MGM', 0.001 union
  select 'total_fat', 'g', 'MC', 0.000001 union
  select 'total_fat', 'g', 'ONZ', 28.3495 union
  select 'total_fat', 'g', 'GRN', 0.06479891
)
update product_nutrition pn
set 
  standardized_unit = c.standardized_unit,
  standardized_value = pn.value * c.multiplier
from conversions c
where lower(pn.nutrient_label) = lower(c.nutrient_label)
  and pn.unit = c.unit;

update product_nutrition
set standardized_unit = 'FLAGGED_UNIT',
    standardized_value = null
where nutrient_label = 'total_fat'
  and standardized_unit is null;

--- vitamin_d ------
with conversions as (
  select 'vitamin_d' as nutrient_label, 'µg' as standardized_unit, 'UG' as unit, 1.0 as multiplier union
  select 'vitamin_d', 'µg', 'MGM', 1000.0 union
  select 'vitamin_d', 'µg', 'GRM', 1000000.0 union
  select 'vitamin_d', 'µg', 'MC', 1.0 union
  select 'vitamin_d', 'µg', 'ONZ', 28349500.0 union
  select 'vitamin_d', 'µg', 'GRN', 64798.91
)
update product_nutrition pn
set 
  standardized_unit = c.standardized_unit,
  standardized_value = pn.value * c.multiplier
from conversions c
where lower(pn.nutrient_label) = lower(c.nutrient_label)
  and pn.unit = c.unit;

update product_nutrition
set standardized_unit = 'FLAGGED_UNIT',
    standardized_value = null
where nutrient_label = 'vitamin_d'
  and standardized_unit is null;
