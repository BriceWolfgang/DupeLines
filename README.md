# DupeLines

This ArcGIS python toolbox will draw lines between any number of features that have a duplicate field value. 
This works for _any_ field in the feature class.

### Requires 10.3, any license, works best with GDBs, does not work with joined data

## For example
 If you have 4,000 streetlights with 200 non unique asset tags, you could run dupelines and select the asset tag field.

Now you have a feature class of individual lines that go between pairs of streetlights with duplicated asset tags. Which might be helpful when fixing an issue like 200 non unique asset tags.

It's also possible to draw lines between all annotations with the the same font, if you’re into that kind of thing.

## Specifics
 * lines will go from the centroid of one feature to the centroid of another.
 * Each line will have the duplicated value as a field, and a count of of which occurrence it represents.
   * For multiple occurrences each pair gets a line.
	* The order of occurrence is random
	* Sorting by location after sorting by the duplicate field would be sweet //ToDo
 * The output will have the same spatial reference as the original feature class 
