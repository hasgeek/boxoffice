const webpack = require('webpack');
const dev = process.env.NODE_ENV || 'production';
const path = require('path');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

function ManifestPlugin(options) {
  this.manifestPath = options.manifestPath
    ? options.manifestPath
    : 'build/manifest.json';
}

ManifestPlugin.prototype.apply = function (compiler) {
  compiler.plugin('done', (stats) => {
    var stats_json = stats.toJson();
    var parsed_stats = {
      assets: stats_json.assetsByChunkName,
    };
    if (stats && stats.hasErrors()) {
      stats_json.errors.forEach((err) => {
        console.error(err);
      });
    }
    require('fs').writeFileSync(
      path.join(__dirname, this.manifestPath),
      JSON.stringify(parsed_stats)
    );
  });
};

module.exports = {
  context: __dirname,
  devtool: dev == 'development' ? 'inline-sourcemap' : false,
  watch: dev == 'development' ? true : false,
  resolve: {
    modules: [__dirname + '/node_modules'],
  },
  entry: {
    main_admin: path.resolve(__dirname, 'js/views/main_admin.js'),
    main_order: path.resolve(__dirname, 'js/views/main_order.js'),
    main_invoice: path.resolve(__dirname, 'js/views/main_invoice.js'),
  },
  output: {
    path: path.resolve(__dirname, '../static/build'),
    publicPath: '/static/build/',
    filename: dev == 'development' ? 'js/[name].js' : 'js/[name].[hash].js',
  },
  module: {
    loaders: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        loader: 'babel-loader',
        query: {
          presets: ['babel-preset-es2015'].map(require.resolve),
        },
      },
    ],
  },
  plugins:
    dev == 'development'
      ? [new ManifestPlugin({ manifestPath: '../static/build/manifest.json' })]
      : [
          new webpack.optimize.UglifyJsPlugin({
            mangle: false,
            sourcemap: false,
          }),
          new CleanWebpackPlugin(),
          new ManifestPlugin({ manifestPath: '../static/build/manifest.json' }),
        ],
};
