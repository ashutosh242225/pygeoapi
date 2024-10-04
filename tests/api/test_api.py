import { useEffect, useRef, useState } from 'react';
import L from 'leaflet';

const MapComponent = () => {
  const mapRef = useRef(null);
  const layersRef = useRef({});
  const layerControl = useRef(null);
  const [activeLayerId, setActiveLayerId] = useState(null); // Track the active layer's collection ID

  useEffect(() => {
    // Initialize the map only once
    if (!mapRef.current) {
      mapRef.current = L.map('map').setView([51.505, -0.09], 13);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(mapRef.current);

      // Initialize layer control
      layerControl.current = L.control.layers(null, null).addTo(mapRef.current);
    }

    // Fetch and display layers from the OGC API
    const fetchOGCLayers = async () => {
      try {
        const response = await fetch('http://localhost:5000/collections');
        const data = await response.json();
        
        data.collections.forEach(collection => {
          // Create a geoJSON layer for each collection
          const layer = L.geoJSON(null, {
            onEachFeature: (feature, layer) => {
              // Bind an empty popup for future dynamic labeling
              layer.bindPopup('');
            }
          }).addTo(mapRef.current);

          // Fetch the features for each collection
          fetch(`http://localhost:5000/collections/${collection.id}/items`)
            .then(res => res.json())
            .then(items => {
              layer.addData(items.features); // Add data to the geoJSON layer
              layersRef.current[collection.id] = layer; // Store the layer
              layerControl.current.addOverlay(layer, collection.title); // Add to layer control with a name
            })
            .catch(err => console.error('Error fetching collection items:', err));
        });

        // Event listeners to control label display
        mapRef.current.on('overlayadd', (e) => {
          const layer = e.layer;
          const collectionId = Object.keys(layersRef.current).find(
            key => layersRef.current[key] === layer
          );
          setActiveLayerId(collectionId); // Set active layer collection ID
          showLabelsForCollection(collectionId, layer);
        });

        mapRef.current.on('overlayremove', (e) => {
          const layer = e.layer;
          hideLabelsForLayer(layer);
        });

      } catch (error) {
        console.error('Error fetching OGC layers:', error);
      }
    };

    // Function to show labels based on the collection.id (active layer)
    const showLabelsForCollection = (collectionId, layer) => {
      layer.eachLayer((featureLayer) => {
        const feature = featureLayer.feature;

        // Customize label content based on collection.id
        let labelContent = '';
        if (collectionId === 'layer1') {
          labelContent = `<b>Label 1:</b> ${feature.properties.property1 || 'N/A'}`;
        } else if (collectionId === 'layer2') {
          labelContent = `<b>Label 2:</b> ${feature.properties.property2 || 'N/A'}`;
        } else {
          // Default or fallback label content
          labelContent = `<b>Default Label:</b> ${feature.properties.defaultProperty || 'N/A'}`;
        }

        // Bind a popup with the label and open it
        featureLayer.bindPopup(labelContent).openPopup();
      });
    };

    // Function to hide labels for the layer (close popups)
    const hideLabelsForLayer = (layer) => {
      layer.eachLayer((featureLayer) => {
        featureLayer.closePopup();
      });
    };

    fetchOGCLayers();
  }, []);

  return <div id="map" style={{ height: '500px', width: '100%' }}></div>;
};

export default MapComponent;
