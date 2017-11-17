var webpack = require('webpack');
var path = require('path');
var dev = process.env.NODE_ENV === "development";

function ManifestPlugin(options){
  this.manifestPath = options.manifestPath;
}

ManifestPlugin.prototype.apply = function(compiler) {
  compiler.plugin('done', stats => {
    var stats_json = stats.toJson();
    var parsed_stats = {
      assets: stats_json.assetsByChunkName,
    }
    require('fs').writeFileSync(
      path.join(__dirname, 'build/manifest.json'),
      JSON.stringify(parsed_stats)
    );
  });
}

module.exports = {
  context: __dirname,
  devtool: dev ? "inline-sourcemap" : false,
  watch: dev ? true : false,
  entry: {
    main_admin: "./js/views/main_admin.js",
    main_order: "./js/views/main_order.js",
    main_invoice: "./js/views/main_invoice.js"
  },
  output: {
    path: __dirname + "/build",
    publicPath: __dirname + "/build",
    filename: dev ? "[name].js" : "[name].[hash].js"
  },
  module: {
    loaders: [{
      test: /\.js$/,
      exclude: /node_modules/,
      loader: 'babel-loader'
    }]
  },
  plugins: dev ? [new ManifestPlugin({manifestPath: ''})] : [
    new webpack.optimize.UglifyJsPlugin({ mangle: false, sourcemap: false }),
    new ManifestPlugin({manifestPath: ''})
  ],
};
