var webpack = require('webpack');
var path = require('path');
var dev = process.env.NODE_ENV === "development";

function ManifestPlugin(options){
  this.manifestPath = options.manifestPath ? options.manifestPath : 'build/manifest.json';
}

ManifestPlugin.prototype.apply = function(compiler) {
  compiler.plugin('done', stats => {
    var stats_json = stats.toJson();
    var parsed_stats = {
      assets: stats_json.assetsByChunkName,
    }
    require('fs').writeFileSync(
      path.join(__dirname, this.manifestPath),
      JSON.stringify(parsed_stats)
    );
  });
}

module.exports = {
  context: __dirname,
  devtool: dev ? "inline-sourcemap" : false,
  watch: dev ? true : false,
  resolve: {
    modules: [
      __dirname + '/node_modules'
    ]
  },
  entry: {
    main_admin: "../assets/js/views/main_admin.js",
    main_order: "../assets/js/views/main_order.js",
    main_invoice: "../assets/js/views/main_invoice.js"
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
      loader: 'babel-loader',
      query: {
        presets: [
          'babel-preset-es2015',
        ].map(require.resolve),
      }
    }]
  },
  plugins: dev ? [new ManifestPlugin({manifestPath: ''})] : [
    new webpack.optimize.UglifyJsPlugin({ mangle: false, sourcemap: false }),
    new ManifestPlugin({manifestPath: ''})
  ],
};
