


Header  = '''#VRML V2.0 utf8
 Viewpoint {
          position    0 -20 0	#the camera positioned to X=0, Y=0 and Z=10
          orientation 1 0 0 1.57	#"default" orientation
          description "top"	#the name of the view,
      }

WorldInfo {
    title "Coterie"
    info  [ "Depth" ]
}
'''

StarSphere = '''
Transform {
    translation $x $y $z
    children[
        Shape{
            appearance Appearance{
                material Material { }
            }
            geometry Sphere {
                radius  $radius  #radius in units
            }
        }
    ]
}
'''



TerrainIndexedFaceSet =''' Shape {
    # $comment
	appearance Appearance {
		texture ImageTexture { url "terrain.png" }

	}

	geometry IndexedFaceSet {
		convex FALSE
		solid TRUE
        ccw TRUE
		coord Coordinate { point [ $points ] }
		coordIndex [ $coordinates ]
        texCoord TextureCoordinate { point [ $tex_coord ]}
	}
}'''



IndexedFaceSet =''' Shape {
    # $comment
	appearance Appearance {
		material Material { }
	}

	geometry IndexedFaceSet {
		convex $convex
		solid $solid
        ccw $ccw
		coord Coordinate { point [ $points ] }
		coordIndex [ $coordinates ]
	}
}'''

DisplayAxes = '''

PROTO SimpleAxis [field SFNode axisAppearance NULL] {
  Transform {
    translation 0 5 0
    children [
      Shape {
        appearance IS axisAppearance
        geometry Cylinder {radius 0.1 height 10}
      }
      Transform {
        translation 0 5.5 0
        children [
          Shape {
            appearance IS axisAppearance
            geometry Cone {bottomRadius 0.25 height 1}
          }
        ]
      }

    ]
  }
}

# Red X-axis

Transform {
  rotation 0 0 1 -1.57080
  children [
    SimpleAxis {
      axisAppearance Appearance {material Material {diffuseColor 1 0 0}}
    }
    Transform {
        translation 0 11 0
        children [
            Shape {
              appearance Appearance {
                  material Material {
                        diffuseColor 1 1 0
                  }
              }
              geometry Text {
                string "X Axis"
                fontStyle FontStyle {
                    size 1
                }
              }
          }
      ]
    }
  ]
}

# Green Y-axis

Transform {
  children [
    SimpleAxis {
      axisAppearance Appearance {material Material {diffuseColor 0 1 0}}
    }
        Transform {
            translation 0 11 0
            children [
                Shape {
                  appearance Appearance {
                      material Material {
                            diffuseColor 1 1 0
                      }
                  }
                  geometry Text {
                    string "Y Axis"
                    fontStyle FontStyle {
                        size 1
                    }
                  }
              }
          ]
        }
  ]
}

# Blue Z-axis

Transform {
  rotation 1 0 0 1.57080
  children [
    SimpleAxis {
      axisAppearance Appearance {material Material {diffuseColor 0 0 1}}
    }
        Transform {
            translation 0 11 0
            children [
                Shape {
                  appearance Appearance {
                      material Material {
                            diffuseColor 1 1 0
                      }
                  }
                  geometry Text {
                    string "Z Axis"
                    fontStyle FontStyle {
                        size 1
                    }
                  }
              }
          ]
        }
  ]
}

# Sphere at origin

Shape {geometry Sphere{}}
'''
