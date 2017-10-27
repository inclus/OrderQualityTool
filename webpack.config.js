//less
//angular
//js
var path = require('path');
var webpack = require('webpack')
module.exports = {
  entry: {
    app: "./uisrc/entry.js"
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
    }]
  },
  plugins: [
    new webpack.ProvidePlugin({
      'window.jQuery': 'jquery',
      'window.$': 'jquery',
      'jQuery': 'jquery'
    }),
    new webpack.NoEmitOnErrorsPlugin()
  ],
  resolve: {
    alias: {
      'jquery': 'jquery/dist/jquery',
      'datatables.net': "datatables.net/js/jquery.dataTables.js",
    }
  }
};
