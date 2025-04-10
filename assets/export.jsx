// Get the active Illustrator document
var doc = app.activeDocument;
doc.artboards.setActiveArtboardIndex(0);
const assetPath = "G:/My Drive/Programming/Python/Piano Typer/assets/";
const allLayers = ["press", "release", "background"];
var halfGreen = doc.layers.getByName("background").pageItems.getByName("half green")
var defaultScale = 1

function exportImage(path, scale) {
    // Export the current group
    // alert("Path: " + path + " Scale: " + scale);
    scale = (typeof scale !== 'undefined') ? scale : defaultScale;
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

function revealAndExport(item, scale) {
    // Shows the item
    item.hidden = false;
    // Export the current group
    exportImage(assetPath + item.parent.name + "/" + item.name + ".png", scale);
    // Hides the item
    item.hidden = true;
}

function actOnFullLayers(layerNames, callback, parameter) {

    for (var i = 0; i < layerNames.length; i++) {
        var layer = doc.layers.getByName(layerNames[i])
        for (var j = 0; j < layer.pageItems.length; j++) {
            var layerItem = layer.pageItems[j];
            callback(layerItem, parameter);
        }
    }
}

function actOnLayerItems(layerName, layerItemNames, callback, parameter) {

    var layer = doc.layers.getByName(layerName)
    for (var i = 0; i < layerItemNames.length; i++) {
        var layerItem = layer.pageItems.getByName(layerItemNames[i]);
        callback(layerItem, parameter);
    }
}

// Function to isolate and export each group on the same artboard
function exportKeys(scale) {
    // Hide all items in all layers
    actOnFullLayers(allLayers, hideItem);

    // halfGreen.hidden = false;

    actOnFullLayers(["press", "release"], revealAndExport, scale);

    halfGreen.hidden = true;

    actOnFullLayers(["release", "background"], showItem);
}

function exportPiano(scale) {
    // Hide all items in all layers
    actOnFullLayers(allLayers, hideItem);
    actOnFullLayers(["release"], showItem);

    exportImage(assetPath + "octave.png", scale);
}

scale = 2
// Run the function
exportKeys(scale);

exportPiano(scale);