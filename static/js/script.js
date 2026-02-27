// Dark Mode
function toggleDark(){
    document.body.classList.toggle("dark");
}

// Map Initialization
const map = L.map("map").setView([20.3540, 85.8179], 15);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{
    attribution:"© OpenStreetMap"
}).addTo(map);

// Markers and Path layers
let startMarker, destMarker, pathLayer;

// Custom Icons
const blueIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

const redIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

// Coordinates display
map.on("mousemove", e => {
    document.getElementById("coords").innerText =
        `Lat: ${e.latlng.lat.toFixed(4)}, Lng: ${e.latlng.lng.toFixed(4)}`;
});

// A* Pathfinding using Backend
async function findPath() {
    const startName = document.getElementById("start").value;
    const destName = document.getElementById("destination").value;
    const resultBox = document.getElementById("result");

    try {
        const response = await fetch('/find_path', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ start: startName, destination: destName })
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert(data.error);
            return;
        }

        // Display results text
        resultBox.innerHTML = `
            <h3>Optimal Path Found!</h3>
            <p><b>Algorithm:</b> ${data.algorithm}</p>
            <p><b>Distance:</b> ${data.distance} km</p>
            <p><b>Nodes Explored:</b> ${data.nodes_explored}</p>
            <p><b>Path:</b> ${data.path.join(" → ")}</p>
        `;

        // Clear existing layers
        if (pathLayer) map.removeLayer(pathLayer);
        if (startMarker) map.removeLayer(startMarker);
        if (destMarker) map.removeLayer(destMarker);

        // Draw Polyline
        const latlngs = data.coordinates.map(c => [c.lat, c.lng]);
        pathLayer = L.polyline(latlngs, {
            color: '#007bff', 
            weight: 6, 
            opacity: 0.8,
            dashArray: '10, 10',
            lineJoin: 'round'
        }).addTo(map);

        // Add Start Marker (Blue)
        const startCoords = campusLocations[startName];
        startMarker = L.marker([startCoords.lat, startCoords.lng], {icon: blueIcon})
            .bindPopup(`<b>Start: ${startName}</b>`)
            .addTo(map);

        // Add Destination Marker (Red)
        const destCoords = campusLocations[destName];
        destMarker = L.marker([destCoords.lat, destCoords.lng], {icon: redIcon})
            .bindPopup(`<b>Destination: ${destName}</b>`)
            .addTo(map);

        // Zoom to path
        map.fitBounds(pathLayer.getBounds(), { padding: [50, 50] });

        // Open popups
        startMarker.openPopup();

    } catch (error) {
        console.error("Error:", error);
        alert("Failed to find path. Is the server running?");
    }
}

// Feedback Modal Logic
function openFeedback(){
    document.getElementById("feedbackModal").style.display="flex";
}
function closeFeedback(){
    document.getElementById("feedbackModal").style.display="none";
}

async function submitFeedback() {
    const name = document.getElementById("fb-name").value;
    const email = document.getElementById("fb-email").value;
    const comment = document.getElementById("fb-comment").value;

    if (!name || !email || !comment) {
        alert("Please fill all fields.");
        return;
    }

    try {
        const response = await fetch('/submit_feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, comment })
        });

        const data = await response.json();
        if (data.success) {
            alert("Feedback sent successfully!");
            closeFeedback();
            document.getElementById("fb-name").value = "";
            document.getElementById("fb-email").value = "";
            document.getElementById("fb-comment").value = "";
        } else {
            alert("Error: " + data.message);
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Failed to send feedback.");
    }
}
