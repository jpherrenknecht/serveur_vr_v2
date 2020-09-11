console.log("Ca marche version leafletbase ")


function arrondi(a,n)
        {return(Math.round(a*10**n)/10**n);}

function pos_dec_mn(pos)
{   abs=Math.abs(pos)
    deg=Math.floor(abs)
    min=Math.floor((abs-deg)*60)
    sec=Math.round(((abs-deg)*60-min)*60)
    return deg+'°'+min+'mn'+sec+'s'
}        

console.log(pos_dec_mn(46.555))

function initialize() {

  
    var map = L.map('map').setView([48.833, 2.333], 7); 
    var osmLayer = L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {   maxZoom: 19});

    var Stamen_TonerLite = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/toner-lite/{z}/{x}/{y}{r}.{ext}', {
    attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    subdomains: 'abcd',
    minZoom: 0,
    maxZoom: 20,
    ext: 'png'
    });

    var Stamen_TerrainBackground = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/terrain-background/{z}/{x}/{y}{r}.{ext}', {
        attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        subdomains: 'abcd',
        minZoom: 0,
        maxZoom: 18,
        ext: 'png'
    });

    var Esri_WorldImagery = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    });


    

    map.addLayer(osmLayer,Stamen_TonerLite,Stamen_TerrainBackground,Esri_WorldImagery);

    latdep=53
    lngdep=2
    var depart    = L.marker([48.6167, -2.7028]).bindPopup('Depart'),
        bouee_2   = L.marker([50.1797, -4.2558]).bindPopup('Bouee 2'),
        bouee_3   = L.marker([49.7539, -0.1069]).bindPopup('Bouee 3'),
        arrivee   = L.marker([51, 2]).bindPopup('Arrivee'),
        test      = L.marker([latdep, lngdep]).bindPopup('Test');
    var marques = L.layerGroup([depart, bouee_2, bouee_3, arrivee,test ]);
    var overlayMaps = {  "Marques": marques};


    // classes pour les icones
    var LeafletIcon=L.Icon.extend({
        options:{
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            shadowSize: [41, 41],
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34]   
                }
        });

    var greenIcon = new LeafletIcon({ iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png'});
    var blackIcon = new LeafletIcon({ iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-black.png'});    
    var redIcon   = new LeafletIcon({ iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png'});        
    
    L.marker([47, -0.09], {icon: greenIcon}).addTo(map);        
    L.marker([48, -0.20], {icon: blackIcon}).addTo(map); 
    L.marker([49, -0.50], {icon: redIcon}).addTo(map); 

    L.control.layers ({
            'osm':osmLayer,
            'Stamen':Stamen_TerrainBackground,         
            'Esri':Esri_WorldImagery.addTo(map)
                    },{
            'Marques':marques.addTo(map)
            }).addTo(map);

 
 
 
 
 
 
 
    L.control.scale({
        metric:true,
        imperial:false,
        position:'topleft'
    }).addTo(map)     



    var poly
poly= new L.Polyline ([[0,0],[1,1]]).setStyle({color:'red',weight:1,});


map.on('click', function(e) {
    latclick=e.latlng.lat
    lngclick=e.latlng.lng
    var popup = L.popup(); 

console.log(e.latlng)
console.log("coucou")    
popup
    .setLatLng(e.latlng)
    .setContent("Latitude      : " +arrondi(e.latlng.lat,4) +" (" +pos_dec_mn(e.latlng.lat) +") <br> Longitude : " +arrondi(e.latlng.lng,4)+" (" +pos_dec_mn(e.latlng.lng) +")" )
    .openOn(map);
    map.removeLayer(poly);
    ligne=[[latdep,lngdep],[latclick,lngclick]]
    poly=new L.polyline(ligne).setStyle({ color: 'red', weight:2, opacity:0.5, }).addTo(map);


// alert("Latitude : " + e.latlng.lat + " Longitude : " + e.latlng.lng)
    });



}
