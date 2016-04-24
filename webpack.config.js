var path = require("path");

var distPath = path.resolve(__dirname, "src/static/js");
var publicPath = "/static/js";
var srcPath = path.resolve(__dirname, "src/fe-src/js");

module.exports = {
    /**
     * pack src/fe-src/js/index.js to src/static/js/index.js
     * pack jquery  to src/static/js/vendors.js
     */
    entry: {
        index : path.join(srcPath, "index.js"),
        vendors : ['jquery']
    },
    
    output: {
        path: distPath,
        filename: "[name].js",
        publicPath: publicPath
    },

    resolve: {
        extensions: ["", ".js", ".jsx", ".json", ".coffee", ".css", ".scss"],
    },
    module: {
        loaders: [
            {
                test: /\.css$/,
                loader: 'style-loader!css-loader'
            }
        ]
    }

}
