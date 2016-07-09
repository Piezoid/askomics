var path = require('path');
var webpack = require("webpack");

class Config {
  constructor() {
    this.entry = {};

    this.output = {
      path: path.join(__dirname, "../askomics/static/"),
      filename: "js/[name].js?[chunkhash]",
      chunkFilename: "js/chunks/[id]-[name].js?[chunkhash]",
      publicPath: "/static/",
    };

    // Enable sourcemaps for debugging webpack's output.
    this.devtool = "source-map";

    this.resolve = {
      // Add '.ts' and '.tsx' as resolvable extensions.
      extensions: ["", ".webpack.js", ".web.js", ".ts", ".tsx", ".js"],
      alias: {},
    };

    this.module = {
      loaders: [{
        test: /\.tsx?$/,
        loader: "ts-loader"
      }],
      preLoaders: [],
      noParse: [],
    };

    this.provides = {}
    this.externals = {}

    this.plugins = [];
  };

  addToChunk(name, module) {
    const modules = this.entry[name] || [];
    if (module instanceof Array) {
      module.forEach(m => modules.push(m));
    } else {
      modules.push(module);
    }
    this.entry[name] = modules;
  }

  addAlias(from, to, noParse = false) {
    this.resolve.alias[from] = to;
    if (noParse) {
      this.module.noParse.push(to);
    }
  }

  addCommonChunk(name, options = {
    minChunks: 2, // Modules must be shared between 2 chunks
  }) {
    this.plugins.push(
      new webpack.optimize.CommonsChunkPlugin(
        Object.assign({}, options, {
          name: name,
          filename: `js/${name}.js`
        })));
  }

  finalize() {
    if (Object.keys(this.provides)
      .length) {
      this.plugins.push(new webpack.ProvidePlugin(this.provides));
    }
    return this;
  }
}

var config = new Config({})

config.addToChunk('main', './js');

config.addCommonChunk('common');

/*
 * Dependencies :
 */

// FileUpload
config.addAlias('tmpl', 'blueimp-tmpl');
config.addAlias('jquery.ui.widget', 'jquery.ui.widget/jquery.ui.widget');

// jQuery
config.provides['$'] = 'jquery';
config.provides['jQuery'] = 'jquery';
//config.addAlias('jquery', 'jquery/dist/jquery.min.js', true);

// handlebars
config.addAlias('handlebars', 'handlebars/dist/cjs/handlebars.js');
//config.addAlias('handlebars', 'handlebars/dist/handlebars.min.js', true);

// Bootstrap
const bsprefix = 'bootstrap/js/';
//const bsprefix = 'bootstrap/dist/js/umd/';
config.addToChunk('common', [
  'affix.js',
  'alert.js',
  'button.js',
  //'carousel.js',
  //'collapse.js',
  'dropdown.js',
  'modal.js',
  //'popover.js',
  //'scrollspy.js',
  //'tab.js',
  'tooltip.js',
  //'util.js',
  //'transition.js',
].map(m => bsprefix + m));


module.exports = config.finalize();
console.log(module.exports);
