import folium
import webbrowser


class Map:
    def __init__(self, center, zoom_start):
        self.center = center
        self.zoom_start = zoom_start
    
    def showMap(self):
        #Create the map
        my_map = folium.Map(tiles="src/main/world_map.jpg")

        #Display the map
        my_map.save("map.html")
        webbrowser.open("map.html")


#Define coordinates of where we want to center our map
coords = [51.5074, 0.1278]
map = Map(center = coords, zoom_start = 13)
map.showMap()