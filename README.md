# DupeLines

This ArcGIS python toolbox will draw lines between any number of features that have a duplicate field value. 
This works for _any_ field in the future class.

### Requires 10.3, works best with GDBs, does not work with joined data

## For example:
 If you have 4,000 streetlights with 200 non unique asset tags, you could run dupelines and select the asset tag field.

Now you have a future class of individual lines that go between streetlights with duplicate asset tags. Which might be helpful when fixing an issue like 200 non unique asset tags. 

Its also possible to draw lines between all the annotations withe the same font, if you’re into that kind of thing.

Specifically lines will go from the centroid of one feature to the centroid of another.
Each line will have the duplicated value as a field, and a count of how many of those values were found
The lines will have the same spatial reference as the original feature class 
