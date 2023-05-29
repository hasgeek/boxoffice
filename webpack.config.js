const webpack = require('webpack');
const ESLintPlugin = require('eslint-webpack-plugin');
const path = require('path');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const { WebpackManifestPlugin } = require('webpack-manifest-plugin');
const fs = require('fs');

const nodeEnv = process.env.NODE_ENV || 'production';

function ManifestPlugin(options) {
  this.manifestPath = options.manifestPath
    ? options.manifestPath
    : 'build/manifest.json';
}

ManifestPlugin.prototype.apply = function (compiler) {
  compiler.plugin('done', (stats) => {
    const statsJson = stats.toJson();
    const parsedStats = {
      assets: statsJson.assetsByChunkName,
    };
    if (stats && stats.hasErrors()) {
      statsJson.errors.forEach((err) => {
        console.error(err);
      });
    }
    fs.writeFileSync(
      path.join(__dirname, this.manifestPath),
      JSON.stringify(parsedStats)
    );
  });
};

module.exports = {
  resolve: {
    fallback: {
      fs: false,
      path: require.resolve('path-browserify'),
    },
  },
  devtool: 'source-map',
  entry: {
    main_admin: path.resolve(
      __dirname,
      'boxoffice/assets/js/views/main_admin.js'
    ),
    main_order: path.resolve(
      __dirname,
      'boxoffice/assets/js/views/main_order.js'
    ),
    main_invoice: path.resolve(
      __dirname,
      'boxoffice/assets/js/views/main_invoice.js'
    ),
    app_css: path.resolve(__dirname, 'boxoffice/assets/sass/app.scss'),
    admin_css: path.resolve(__dirname, 'boxoffice/assets/sass/admin.scss'),
  },
  output: {
    path: path.resolve(__dirname, 'boxoffice/static/build'),
    publicPath: '/static/build/',
    filename: 'js/[name].[chunkhash].js',
  },
  module: {
    rules: [
      {
        enforce: 'pre',
        test: /\.js$/,
        exclude: /node_modules/,
        loader: 'babel-loader',
        options: {
          plugins: ['@babel/plugin-syntax-dynamic-import'],
        },
      },
      {
        test: /\.scss$/,
        exclude: /node_modules/,
        use: [
          {
            loader: 'file-loader',
            options: { outputPath: 'css/', name: '[name].[hash].css' },
          },
          'sass-loader',
        ],
      },
    ],
  },
  plugins: [
    new ESLintPlugin({
      fix: true,
    }),
    new webpack.DefinePlugin({
      'process.env': { NODE_ENV: JSON.stringify(nodeEnv) },
    }),
    new CleanWebpackPlugin({
      root: path.join(__dirname, 'boxoffice/static'),
    }),
    new WebpackManifestPlugin({
      fileName: path.join(__dirname, 'boxoffice/static/build/manifest.json'),
    }),
  ],
};
