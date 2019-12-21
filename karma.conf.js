var path = require('path');
module.exports = function (config) {
  config.set({
    basePath: '',
    frameworks: ['jasmine'],
    exclude: [],
    reporters: ['progress', 'coverage-istanbul'],
    port: 9876,
    colors: true,
    logLevel: config.LOG_INFO,
    autoWatch: false,
    browsers: ['PhantomJS'],
    singleRun: true,
    concurrency: Infinity,
    files: [
      'uisrc/test-entry.js'
    ],

    preprocessors: {
      'uisrc/test-entry.js': 'webpack'
    },

    webpack: {
      module: {
        rules: [{
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
        },{
          test: /\.js$/,
          use: { loader: 'istanbul-instrumenter-loader' },
          include: path.resolve('./uisrc/')
        }]
      },
    },

    webpackMiddleware: {
      stats: 'errors-only'
    }
  });
};