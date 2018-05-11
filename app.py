from flask import Flask, render_template, request, send_file
from werkzeug import secure_filename
import pandas as pd
from geopy.geocoders import Nominatim
import folium


app = Flask(__name__)


@app.route("/")
def start_page():
    return render_template("start_page.html")


@app.route("/success", methods=["POST"])
def success():
    global file
    if request.method == "POST":
        file = request.files["file"]
        file.save(secure_filename("uploaded_" + file.filename))
        f = "uploaded_" + file.filename
        try:
            df = pd.read_csv(f, index_col=0)
            df.index.name = None
            try:
                for col in df.columns:
                    if col == 'address':
                        df.rename(columns={'address': 'Address'}, inplace=True)

                nom = Nominatim()
                addresses = df['Address']
                latitude = []
                longitude = []

                for address in addresses:
                    try:
                        location = nom.geocode(address)
                        lat = location.latitude
                        lon = location.longitude
                        latitude.append(str(lat))
                        longitude.append(str(lon))

                    except:
                        latitude.append('None')
                        longitude.append('None')
                        pass

                df['Latitude'] = latitude
                df['Longitude'] = longitude
                df.to_csv(f, sep='\t', encoding='utf-8')

                map_csv = folium.Map(location=[37.756023, -122.432088], zoom_start=13)
                fgv = folium.FeatureGroup(name="Location of places extracted from csv file")

                for lat, lon, ad in zip(latitude, longitude, addresses):
                    try:
                        fgv.add_child(folium.Marker(location=[float(lat), float(lon)], popup=ad,
                                                    icon=folium.Icon(color='green')))

                    except:
                        pass
                map_csv.add_child(fgv)
                map_csv.save("templates/map.html")

                return render_template("start_page.html", btn="download.html",
                                       button="my_map.html", table=df.to_html(classes='table'))
            except KeyError:
                return render_template("start_page.html",
                            text="Oops! Seems like you've got an error. "
                                 "Please make sure you have an address column in your CSV file or check its spelling.")
        except:
            return render_template("start_page.html",
                                   text="Oops! Seems like you've got an error. Please check extension of your file (must be csv).")


@app.route("/download")
def download():
    return send_file("uploaded_" + file.filename, attachment_filename="yourfile.csv", as_attachment=True)


@app.route("/map")
def view_map():
    return render_template("map.html")


if __name__ == '__main__':
    app.debug = False
    app.run()
