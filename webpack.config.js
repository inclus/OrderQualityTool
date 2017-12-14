//less
//angular
//js
var path = require('path');
var webpack = require('webpack')
var CompressionPlugin = require("compression-webpack-plugin")
var WriteFilePlugin = require('write-file-webpack-plugin');

var isDevServer = process.argv.find(v => v.includes('livereload'));

var entryFiles = ["./uisrc/entry.js"];
var testDefinitionEntryFiles = ["./uisrc/test-definition/entry"];
if (isDevServer) {
    console.log('Dev server')
    entryFiles.push("webpack-dev-server/client?http://localhost:3030")
    testDefinitionEntryFiles.push("webpack-dev-server/client?http://localhost:3030")
    entryFiles.push('webpack/hot/only-dev-server')
    testDefinitionEntryFiles.push('webpack/hot/only-dev-server')
}

module.exports = {
    devtool: 'inline-source-map',
    entry: {
        app: entryFiles,
        "test.definition": testDefinitionEntryFiles,

  },
  output: {
    path: path.join(__dirname, "dashboard/static/dist"),
    filename: "[name].bundle.js",
    publicPath: "/static/dist/"
  },
  module: {
    loaders: [{
      test: /\.less$/,
      loader: "style-loader!css-loader!less-loader"
    }, {
      test: /\.css$/,
      loader: "style-loader!css-loader"
    }, {
      test: /\.png$/,
      loader: "url-loader?limit=100000"
    }, {
      test: /\.jpg$/,
      loader: "file-loader"
    }, {
      test: /\.(ttf|eot|svg|woff(2)?)(\?[a-z0-9]+)?$/,
      loader: 'file-loader'
    },
    {
      test: /\.(html)$/,
      loader: 'html-loader'
    }, {
            test: /\.js$/,
            exclude: /node_modules/,
            loader: 'eslint-loader',
            options: {
                fix: true
            }
        }]
  },
  plugins: [
    new webpack.ProvidePlugin({
      'window.jQuery': 'jquery',
      'window.$': 'jquery',
      'jQuery': 'jquery'
    }),
    new webpack.HotModuleReplacementPlugin(),
    new webpack.NoEmitOnErrorsPlugin(),
    new CompressionPlugin(),
    new WriteFilePlugin()
  ],
  resolve: {
    alias: {
      'jquery': 'jquery/dist/jquery',
      'datatables.net': "datatables.net/js/jquery.dataTables.js",
    }
  }
};
