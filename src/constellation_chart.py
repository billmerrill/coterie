from bokeh.plotting import figure, output_file, show
from bokeh.models import Label, WheelZoomTool, Segment


class ConstellationChart(object):

    def __init__(self, constellation=None, featured_stars=None):
        self.constellation = constellation
        self.featured_stars = featured_stars

    def chart2D(self):
        # cons, stars, connections):
        star_x = []
        star_y = []
        for s in sorted(self.constellation.stars):
            projected = self.constellation.stars[s].projected
            if projected:
                star_x.append(projected[0])
                star_y.append(projected[1])

        output_file("stars.html")
        p = figure(plot_width=800, plot_height=800, title='orion')
        p.toolbar.active_scroll = WheelZoomTool()
        for star in self.constellation.stars.values():
            if self.featured_stars and star.hyg_id in self.featured_stars:
                circle_color = "#000000"
            else:
                circle_color = "#cccccc"
            p.circle(star.projected[0], star.projected[1],
                     name=star.key, size=10, color=circle_color)
            p.add_layout(Label(x=star.projected[0], y=star.projected[1],
                               text="{}:{} {:.2f}".format(star.hyg_id, star.key,
                               star.magnitude), text_color="#999999"))
        for connection in self.constellation.connections:
            a = self.constellation.get_star(connection[0])
            b = self.constellation.get_star(connection[1])
            glyph = Segment(x0=a.projected[0], y0=a.projected[1], x1=b.projected[0],
                            y1=b.projected[1], line_color="#aaeeaa", line_width=4)
            p.add_glyph(glyph)

        show(p, browser="safari", new="window")
