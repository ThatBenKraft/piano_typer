// Get the active Illustrator document
var doc = app.activeDocument;
doc.artboards.setActiveArtboardIndex(2);
const assetPath = "G:/My Drive/Programming/Python/piano-typer/assets/";
// Function to isolate and export each group on the same artboard
/**
 * @param {float} scale - The export scale
 */
function exportKeys(scale) {
    const actions = ["press", "release"];
    // Hide all items in both layers
    actOnItemsInLayers(actions, hideItem);

    actOnItemsInLayers(actions, revealAndExport);
    // Show all items in both layers
    actOnItemsInLayers(actions, showItem);
}

function exportPiano(scale) {
    // Hide all items in both layers
    actOnItemsInLayers(["press"], hideItem);
    actOnItemsInLayers(["release", "background"], showItem);

    exportImage(assetPath + "octave.png", scale);

}

function exportImage(path, scale) {
    // Export the current group
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
    item.hidden = false;
    // Export the current group
    exportImage(assetPath + targetLayer.name + "/" + item.name + ".png", scale);
    // Hides the item
    item.hidden = true;
}

function actOnItemsInLayers(layers, callback) {

    for (var a = 0; a < layers.length; a++) {
        layerItems = doc.layers.getByName(layers[a]).pageItems;
        for (var i = 0; i < layerItems.length; i++) {
            callback(layerItems[i]);
        }
    }
}

// Run the function
exportKeys(scale = 1);

exportPiano(scale = 1);