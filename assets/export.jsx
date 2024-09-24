// Get the active Illustrator document
var doc = app.activeDocument;
doc.artboards.setActiveArtboardIndex(0);
const assetPath = "G:/My Drive/Programming/Python/Piano Typer/assets/";
const allLayers = ["press", "release", "background"];
var halfGreen = doc.layers.getByName("background").pageItems.getByName("half green")

function exportImage(path, scale) {
    // Export the current group
    scale = (typeof scale !== 'undefined') ? scale : 1;
    var options = new ExportOptionsPNG24();
    options.antiAliasing = true; // Enable anti-aliasing for smoother edges
    options.artBoardClipping = true; // Export only the artboard content
    options.horizontalScale = scale * 100;
    options.verticalScale = scale * 100;
    var file = new File(path);
    doc.exportFile(file, ExportType.PNG24, options);
}

function hideItem(item) {
    item.hidden = true;
}

function showItem(item) {
    item.hidden = false;
}

function revealAndExport(item) {
    // Shows the item
    item.hidden = false;
    // Export the current group
    exportImage(assetPath + item.parent.name + "/" + item.name + ".png");
    // Hides the item
    item.hidden = true;
}

function actOnFullLayers(layerNames, callback, parameters) {

    for (var i = 0; i < layerNames.length; i++) {
        var layer = doc.layers.getByName(layerNames[i])
        for (var j = 0; j < layer.pageItems.length; j++) {
            var layerItem = layer.pageItems[j];
            callback(layerItem, parameters);
        }
    }
}

function actOnLayerItems(layerName, layerItemNames, callback, parameters) {

    var layer = doc.layers.getByName(layerName)
    for (var i = 0; i < layerItemNames.length; i++) {
        var layerItem = layer.pageItems.getByName(layerItemNames[i]);
        callback(layerItem, parameters);
    }
}

// Function to isolate and export each group on the same artboard
function exportKeys() {
    // Hide all items in all layers
    actOnFullLayers(allLayers, hideItem);

    // halfGreen.hidden = false;

    actOnFullLayers(["press", "release"], revealAndExport);

    halfGreen.hidden = true;

    actOnFullLayers(["release", "background"], showItem);
}

function exportPiano() {
    // Hide all items in all layers
    actOnFullLayers(allLayers, hideItem);
    actOnFullLayers(["release"], showItem);

    exportImage(assetPath + "octave.png");
}

// Run the function
exportKeys();

// exportPiano();