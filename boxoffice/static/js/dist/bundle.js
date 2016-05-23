(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
"use strict";

var Router = require("./router").Router;

$(function () {
  var appRouter = new Router();
  Backbone.history.start({ pushState: true, root: "/admin/" });
  window.eventBus = _.clone(Backbone.Events);
  window.eventBus.on("navigate", function (msg) {
    appRouter.navigate(msg, { trigger: true });
  });
});

},{"./router":11}],2:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
var IndexModel = Backbone.Model.extend({
  url: function url() {
    return "/admin/dashboard";
  }
});
exports.IndexModel = IndexModel;

},{}],3:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
var ItemCollectionModel = Backbone.Model.extend({
  url: function url(id) {
    return "/admin/ic/" + this.get("id");
  }
});
exports.ItemCollectionModel = ItemCollectionModel;

},{}],4:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
var OrgModel = Backbone.Model.extend({
  url: function url(name) {
    console.log(this.get("name"));
    return "/admin/o/" + this.get("name");
  }
});
exports.OrgModel = OrgModel;

},{}],5:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
var IndexTemplate = "\n  {{#orgs}}\n    <a href=\"javascript:void(0)\" on-click=\"navigate\">{{title}}</a>\n  {{/}}\n";
exports.IndexTemplate = IndexTemplate;

},{}],6:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
var TableTemplate = "\n  <div class=\"table-responsive stats\">\n    <table class=\"table table-bordered table-hover stats-table\">\n      <thead>\n        <tr class=\"info\">\n          <th>#</th>\n          <th>Item</th>\n          <th>Available</th>\n          <th>Sold</th>\n          <th>Free</th>\n          <th>Cancelled</th>\n          <th>Current Price</th>\n          <th>Net Sales</th>\n        </tr>\n      </thead>\n      <tbody>\n        {{#items}}\n          <tr>\n            <td>{{ @index + 1 }}</td>\n            <td>{{ title }}</td>\n            <td>{{ available }}</td>\n            <td>{{ sold }}</td>\n            <td>{{ free }}</td>\n            <td>{{ cancelled }}</td>\n            <td>{{ current_price }}</td>\n            <td>{{ net_sales }}</td>\n          </tr>\n        {{/}}\n      </tbody>\n    </table>\n  </div>\n";

exports.TableTemplate = TableTemplate;
var AggChartTemplate = "\n  <div id=\"chart\" class=\"c3\" style=\"max-height: 280px; position: relative;\">\n  </div>\n";

exports.AggChartTemplate = AggChartTemplate;
var ItemCollectionTemplate = "\n  <br>\n  <div class=\"row\">\n    <div class=\"col-md-4\">\n      <div class=\"panel panel-default\">\n        <div class=\"panel-heading\">\n          <h3 class=\"panel-title\">Net Sales</h3>\n        </div>\n        <div class=\"panel-body\">\n          {{net_sales}}\n        </div>\n      </div>\n    </div>\n  </div>\n  <hr>\n  <AggChartComponent></AggChartComponent>\n  <hr>\n  <TableComponent></TableComponent>\n";
exports.ItemCollectionTemplate = ItemCollectionTemplate;

},{}],7:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
var orgTemplate = "\n  <ul>\n    {{#item_collections}}\n      <li>\n        <a href=\"javascript:void(0)\" on-click=\"navigate\">{{title}}</a>\n      </li>\n    {{/}}\n  </ul>\n";
exports.orgTemplate = orgTemplate;

},{}],8:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});

var IndexModel = require("../models/index.js").IndexModel;

var IndexTemplate = require("../templates/index.html.js").IndexTemplate;

var IndexView = {
  render: function render() {
    this.indexModel = new IndexModel();
    this.indexModel.fetch().then(function (data) {
      this.ractive = new Ractive({
        el: "#main-content-area",
        template: IndexTemplate,
        data: {
          orgs: data.orgs
        }
      });
      this.ractive.on("navigate", function (event, method) {
        // console.log(event.context.url);
        eventBus.trigger("navigate", event.context.url);
      });
    });
  }
};
exports.IndexView = IndexView;

},{"../models/index.js":2,"../templates/index.html.js":5}],9:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});

var ItemCollectionModel = require("../models/item_collection.js").ItemCollectionModel;

var _templatesItem_collectionHtmlJs = require("../templates/item_collection.html.js");

var TableTemplate = _templatesItem_collectionHtmlJs.TableTemplate;
var AggChartTemplate = _templatesItem_collectionHtmlJs.AggChartTemplate;
var ItemCollectionTemplate = _templatesItem_collectionHtmlJs.ItemCollectionTemplate;

// Components
// table
// chart

var TableComponent = Ractive.extend({
  isolated: false,
  template: TableTemplate
});

var AggChartComponent = Ractive.extend({
  template: AggChartTemplate,
  oncomplete: function oncomplete() {
    var date_item_counts = this.parent.get("date_item_counts");
    var items = this.parent.get("items");
    var date_sales = this.parent.get("date_sales");
    var dates = ["x"];
    var item_counts = {};
    var date_sales_column = ["date_sales"];
    for (var item_date in date_item_counts) {
      (function (item_date) {
        dates.push(item_date);
        date_sales_column.push(date_sales[item_date]);
        items.forEach(function (item) {
          if (!item_counts[item.id]) {
            item_counts[item.id] = [];
          }
          if (date_item_counts[item_date].hasOwnProperty(item.id)) {
            // If an item has been bought on this item_date
            item_counts[item.id].push(date_item_counts[item_date][item.id]);
          } else {
            // Item not bought on this date
            item_counts[item.id].push(0);
          }
        });
      })(item_date);
    }

    var columns = [dates];
    items.forEach(function (item) {
      columns.push([item.title].concat(item_counts[item.id]));
    });

    var bar_graph_headers = columns.map(function (col) {
      return col[0];
    }).filter(function (header) {
      return header !== "x";
    });

    columns.push(date_sales_column);

    this.chart = c3.generate({
      data: {
        x: "x",
        columns: columns,
        type: "bar",
        types: {
          date_sales: "line"
        },
        groups: [bar_graph_headers],
        axes: {
          date_sales: "y2"
        }
      },
      bar: {
        width: {
          ratio: 0.5 // this makes bar width 50% of length between ticks
        }
      },
      axis: {
        x: {
          type: "timeseries",
          tick: {
            format: "%d-%m"
          }
        },
        y2: {
          show: true
        }
      }
    });
  }
});

var ItemCollectionView = {
  init: function init(data) {
    var _this = this;

    this.ractive = new Ractive({
      el: "#main-content-area",
      template: ItemCollectionTemplate,
      data: {
        items: this.model.get("items"),
        date_item_counts: this.model.get("date_item_counts"),
        date_sales: this.model.get("date_sales"),
        net_sales: this.model.get("net_sales")
      },
      components: { TableComponent: TableComponent, AggChartComponent: AggChartComponent }
    });

    this.model.on("change:items", function (model, items) {
      return _this.ractive.set("items", items);
    });

    this.ractive.on("navigate", function (event, method) {
      // kill interval
      clearInterval(this.intervalId);
      eventBus.trigger("navigate", event.context.url);
    });
    window.addEventListener("popstate", function (event) {
      // kill interval
      clearInterval(_this.intervalId);
    });
  },
  fetch: function fetch() {
    var _this = this;

    return this.model.fetch().then(function (data) {
      _this.model.set("items", data.items);
      _this.model.set("date_item_counts", data.date_item_counts);
      _this.model.set("date_sales", data.date_sales);
      _this.model.set("net_sales", data.net_sales);
    });
  },
  refresh: function refresh() {
    this.fetch();
  },
  render: function render(initData) {
    var _this = this;

    this.model = new ItemCollectionModel({
      id: initData.id
    });

    this.fetch().then(function () {
      return _this.init();
    });

    this.intervalId = setInterval(function () {
      return _this.refresh();
    }, 3000);
  }
};
exports.ItemCollectionView = ItemCollectionView;

},{"../models/item_collection.js":3,"../templates/item_collection.html.js":6}],10:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});

var OrgModel = require("../models/org.js").OrgModel;

// import {renderview} from './renderview.js';

var orgTemplate = require("../templates/org.html.js").orgTemplate;

var OrgView = {
  render: function render(org) {
    this.orgModel = new OrgModel({
      name: org.name
    });
    this.orgModel.fetch().then(function (data) {
      this.ractive = new Ractive({
        el: "#main-content-area",
        // template: '#org-content-template',
        template: orgTemplate,
        data: {
          name: data.name,
          item_collections: data.item_collections
        }
      });
      this.ractive.on("navigate", function (event, method) {
        // console.log(event.context.url);
        eventBus.trigger("navigate", event.context.url);
      });
    });
  }
};
exports.OrgView = OrgView;

},{"../models/org.js":4,"../templates/org.html.js":7}],11:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});

var IndexView = require("./index.js").IndexView;

var OrgView = require("./org.js").OrgView;

var ItemCollectionView = require("./item_collection.js").ItemCollectionView;

var Router = Backbone.Router.extend({
  routes: {
    "": "index",
    "o/:org": "org",
    "ic/:icId": "item_collection"
  },
  index: function index() {
    IndexView.render();
  },
  org: (function (_org) {
    var _orgWrapper = function org(_x) {
      return _org.apply(this, arguments);
    };

    _orgWrapper.toString = function () {
      return _org.toString();
    };

    return _orgWrapper;
  })(function (org) {
    OrgView.render({ name: org });
  }),
  item_collection: function item_collection(icId) {
    ItemCollectionView.render({ id: icId });
  }
});
exports.Router = Router;

},{"./index.js":8,"./item_collection.js":9,"./org.js":10}]},{},[1])
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCIvaG9tZS9zaHJleWFzL2Rldi9oYXNnZWVrL2JveG9mZmljZS9ib3hvZmZpY2Uvc3RhdGljL2pzL3ZpZXdzL21haW4uanMiLCIvaG9tZS9zaHJleWFzL2Rldi9oYXNnZWVrL2JveG9mZmljZS9ib3hvZmZpY2Uvc3RhdGljL2pzL21vZGVscy9pbmRleC5qcyIsIi9ob21lL3NocmV5YXMvZGV2L2hhc2dlZWsvYm94b2ZmaWNlL2JveG9mZmljZS9zdGF0aWMvanMvbW9kZWxzL2l0ZW1fY29sbGVjdGlvbi5qcyIsIi9ob21lL3NocmV5YXMvZGV2L2hhc2dlZWsvYm94b2ZmaWNlL2JveG9mZmljZS9zdGF0aWMvanMvbW9kZWxzL29yZy5qcyIsIi9ob21lL3NocmV5YXMvZGV2L2hhc2dlZWsvYm94b2ZmaWNlL2JveG9mZmljZS9zdGF0aWMvanMvdGVtcGxhdGVzL2luZGV4Lmh0bWwuanMiLCIvaG9tZS9zaHJleWFzL2Rldi9oYXNnZWVrL2JveG9mZmljZS9ib3hvZmZpY2Uvc3RhdGljL2pzL3RlbXBsYXRlcy9pdGVtX2NvbGxlY3Rpb24uaHRtbC5qcyIsIi9ob21lL3NocmV5YXMvZGV2L2hhc2dlZWsvYm94b2ZmaWNlL2JveG9mZmljZS9zdGF0aWMvanMvdGVtcGxhdGVzL29yZy5odG1sLmpzIiwiL2hvbWUvc2hyZXlhcy9kZXYvaGFzZ2Vlay9ib3hvZmZpY2UvYm94b2ZmaWNlL3N0YXRpYy9qcy92aWV3cy9pbmRleC5qcyIsIi9ob21lL3NocmV5YXMvZGV2L2hhc2dlZWsvYm94b2ZmaWNlL2JveG9mZmljZS9zdGF0aWMvanMvdmlld3MvaXRlbV9jb2xsZWN0aW9uLmpzIiwiL2hvbWUvc2hyZXlhcy9kZXYvaGFzZ2Vlay9ib3hvZmZpY2UvYm94b2ZmaWNlL3N0YXRpYy9qcy92aWV3cy9vcmcuanMiLCIvaG9tZS9zaHJleWFzL2Rldi9oYXNnZWVrL2JveG9mZmljZS9ib3hvZmZpY2Uvc3RhdGlj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QyxPQUFPLENBQUMsVUFBVSxFQUFFLEtBQUssQ0FBQyxPQUFPLENBQUMsR0FBRyxDQUFDLENBQUM7T0FDakQsQ0FBQyxDQUFDO0tBQ0osQ0FBQyxDQUFDO0dBRUo7Q0FDRixDQUFBO1FBdEJZLE9BQU8sR0FBUCxPQUFPOzs7Ozs7Ozs7SUNKWixTQUFTLFdBQU8sWUFBWSxFQUE1QixTQUFTOztJQUNULE9BQU8sV0FBTyxVQUFVLEVBQXhCLE9BQU87O0lBQ1Asa0JBQWtCLFdBQU8sc0JBQXNCLEVBQS9DLGtCQUFrQjs7QUFFbkIsSUFBTSxNQUFNLEdBQUcsUUFBUSxDQUFDLE1BQU0sQ0FBQyxNQUFNLENBQUM7QUFDM0MsUUFBTSxFQUFFO0FBQ04sTUFBRSxFQUFFLE9BQU87QUFDWCxZQUFRLEVBQUUsS0FBSztBQUNmLGNBQVUsRUFBRSxpQkFBaUI7R0FDOUI7QUFDRCxPQUFLLEVBQUUsaUJBQVc7QUFDaEIsYUFBUyxDQUFDLE1BQU0sRUFBRSxDQUFDO0dBQ3BCO0FBQ0QsS0FBRzs7Ozs7Ozs7OztLQUFFLFVBQVMsR0FBRyxFQUFDO0FBQ2hCLFdBQU8sQ0FBQyxNQUFNLENBQUMsRUFBQyxJQUFJLEVBQUUsR0FBRyxFQUFDLENBQUMsQ0FBQztHQUM3QixDQUFBO0FBQ0QsaUJBQWUsRUFBRSx5QkFBUyxJQUFJLEVBQUM7QUFDN0Isc0JBQWtCLENBQUMsTUFBTSxDQUFDLEVBQUMsRUFBRSxFQUFFLElBQUksRUFBQyxDQUFDLENBQUM7R0FDdkM7Q0FDRixDQUFDLENBQUM7UUFmVSxNQUFNLEdBQU4sTUFBTSIsImZpbGUiOiJnZW5lcmF0ZWQuanMiLCJzb3VyY2VSb290IjoiIiwic291cmNlc0NvbnRlbnQiOlsiKGZ1bmN0aW9uIGUodCxuLHIpe2Z1bmN0aW9uIHMobyx1KXtpZighbltvXSl7aWYoIXRbb10pe3ZhciBhPXR5cGVvZiByZXF1aXJlPT1cImZ1bmN0aW9uXCImJnJlcXVpcmU7aWYoIXUmJmEpcmV0dXJuIGEobywhMCk7aWYoaSlyZXR1cm4gaShvLCEwKTt2YXIgZj1uZXcgRXJyb3IoXCJDYW5ub3QgZmluZCBtb2R1bGUgJ1wiK28rXCInXCIpO3Rocm93IGYuY29kZT1cIk1PRFVMRV9OT1RfRk9VTkRcIixmfXZhciBsPW5bb109e2V4cG9ydHM6e319O3Rbb11bMF0uY2FsbChsLmV4cG9ydHMsZnVuY3Rpb24oZSl7dmFyIG49dFtvXVsxXVtlXTtyZXR1cm4gcyhuP246ZSl9LGwsbC5leHBvcnRzLGUsdCxuLHIpfXJldHVybiBuW29dLmV4cG9ydHN9dmFyIGk9dHlwZW9mIHJlcXVpcmU9PVwiZnVuY3Rpb25cIiYmcmVxdWlyZTtmb3IodmFyIG89MDtvPHIubGVuZ3RoO28rKylzKHJbb10pO3JldHVybiBzfSkiLCJcbmltcG9ydCB7Um91dGVyfSBmcm9tICcuL3JvdXRlcic7XG5cblxuJChmdW5jdGlvbigpe1xuICBsZXQgYXBwUm91dGVyID0gbmV3IFJvdXRlcigpO1xuICBCYWNrYm9uZS5oaXN0b3J5LnN0YXJ0KHtwdXNoU3RhdGU6IHRydWUsIHJvb3Q6IFwiL2FkbWluL1wifSk7XG4gIHdpbmRvdy5ldmVudEJ1cyA9IF8uY2xvbmUoQmFja2JvbmUuRXZlbnRzKTtcbiAgd2luZG93LmV2ZW50QnVzLm9uKCduYXZpZ2F0ZScsIGZ1bmN0aW9uKG1zZyl7XG4gICAgYXBwUm91dGVyLm5hdmlnYXRlKG1zZywge3RyaWdnZXI6IHRydWV9KTtcbiAgfSlcbn0pO1xuXG4iLCJcbmV4cG9ydCBjb25zdCBJbmRleE1vZGVsID0gQmFja2JvbmUuTW9kZWwuZXh0ZW5kKHtcbiAgdXJsIDogZnVuY3Rpb24oKXtcbiAgICByZXR1cm4gJy9hZG1pbi9kYXNoYm9hcmQnO1xuICB9XG59KTtcbiIsIlxuZXhwb3J0IGNvbnN0IEl0ZW1Db2xsZWN0aW9uTW9kZWwgPSBCYWNrYm9uZS5Nb2RlbC5leHRlbmQoe1xuICB1cmwgOiBmdW5jdGlvbihpZCl7XG4gICAgcmV0dXJuICcvYWRtaW4vaWMvJyArIHRoaXMuZ2V0KCdpZCcpO1xuICB9XG59KTtcbiIsIlxuZXhwb3J0IGNvbnN0IE9yZ01vZGVsID0gQmFja2JvbmUuTW9kZWwuZXh0ZW5kKHtcbiAgdXJsIDogZnVuY3Rpb24obmFtZSl7XG4gICAgY29uc29sZS5sb2codGhpcy5nZXQoJ25hbWUnKSk7XG4gICAgcmV0dXJuICcvYWRtaW4vby8nICsgdGhpcy5nZXQoJ25hbWUnKTtcbiAgfVxufSk7XG4iLCJleHBvcnQgY29uc3QgSW5kZXhUZW1wbGF0ZSA9IGBcbiAge3sjb3Jnc319XG4gICAgPGEgaHJlZj1cImphdmFzY3JpcHQ6dm9pZCgwKVwiIG9uLWNsaWNrPVwibmF2aWdhdGVcIj57e3RpdGxlfX08L2E+XG4gIHt7L319XG5gXG4iLCJleHBvcnQgY29uc3QgVGFibGVUZW1wbGF0ZSA9IGBcbiAgPGRpdiBjbGFzcz1cInRhYmxlLXJlc3BvbnNpdmUgc3RhdHNcIj5cbiAgICA8dGFibGUgY2xhc3M9XCJ0YWJsZSB0YWJsZS1ib3JkZXJlZCB0YWJsZS1ob3ZlciBzdGF0cy10YWJsZVwiPlxuICAgICAgPHRoZWFkPlxuICAgICAgICA8dHIgY2xhc3M9XCJpbmZvXCI+XG4gICAgICAgICAgPHRoPiM8L3RoPlxuICAgICAgICAgIDx0aD5JdGVtPC90aD5cbiAgICAgICAgICA8dGg+QXZhaWxhYmxlPC90aD5cbiAgICAgICAgICA8dGg+U29sZDwvdGg+XG4gICAgICAgICAgPHRoPkZyZWU8L3RoPlxuICAgICAgICAgIDx0aD5DYW5jZWxsZWQ8L3RoPlxuICAgICAgICAgIDx0aD5DdXJyZW50IFByaWNlPC90aD5cbiAgICAgICAgICA8dGg+TmV0IFNhbGVzPC90aD5cbiAgICAgICAgPC90cj5cbiAgICAgIDwvdGhlYWQ+XG4gICAgICA8dGJvZHk+XG4gICAgICAgIHt7I2l0ZW1zfX1cbiAgICAgICAgICA8dHI+XG4gICAgICAgICAgICA8dGQ+e3sgQGluZGV4ICsgMSB9fTwvdGQ+XG4gICAgICAgICAgICA8dGQ+e3sgdGl0bGUgfX08L3RkPlxuICAgICAgICAgICAgPHRkPnt7IGF2YWlsYWJsZSB9fTwvdGQ+XG4gICAgICAgICAgICA8dGQ+e3sgc29sZCB9fTwvdGQ+XG4gICAgICAgICAgICA8dGQ+e3sgZnJlZSB9fTwvdGQ+XG4gICAgICAgICAgICA8dGQ+e3sgY2FuY2VsbGVkIH19PC90ZD5cbiAgICAgICAgICAgIDx0ZD57eyBjdXJyZW50X3ByaWNlIH19PC90ZD5cbiAgICAgICAgICAgIDx0ZD57eyBuZXRfc2FsZXMgfX08L3RkPlxuICAgICAgICAgIDwvdHI+XG4gICAgICAgIHt7L319XG4gICAgICA8L3Rib2R5PlxuICAgIDwvdGFibGU+XG4gIDwvZGl2PlxuYFxuXG5leHBvcnQgY29uc3QgQWdnQ2hhcnRUZW1wbGF0ZSA9IGBcbiAgPGRpdiBpZD1cImNoYXJ0XCIgY2xhc3M9XCJjM1wiIHN0eWxlPVwibWF4LWhlaWdodDogMjgwcHg7IHBvc2l0aW9uOiByZWxhdGl2ZTtcIj5cbiAgPC9kaXY+XG5gXG5cbmV4cG9ydCBjb25zdCBJdGVtQ29sbGVjdGlvblRlbXBsYXRlID0gYFxuICA8YnI+XG4gIDxkaXYgY2xhc3M9XCJyb3dcIj5cbiAgICA8ZGl2IGNsYXNzPVwiY29sLW1kLTRcIj5cbiAgICAgIDxkaXYgY2xhc3M9XCJwYW5lbCBwYW5lbC1kZWZhdWx0XCI+XG4gICAgICAgIDxkaXYgY2xhc3M9XCJwYW5lbC1oZWFkaW5nXCI+XG4gICAgICAgICAgPGgzIGNsYXNzPVwicGFuZWwtdGl0bGVcIj5OZXQgU2FsZXM8L2gzPlxuICAgICAgICA8L2Rpdj5cbiAgICAgICAgPGRpdiBjbGFzcz1cInBhbmVsLWJvZHlcIj5cbiAgICAgICAgICB7e25ldF9zYWxlc319XG4gICAgICAgIDwvZGl2PlxuICAgICAgPC9kaXY+XG4gICAgPC9kaXY+XG4gIDwvZGl2PlxuICA8aHI+XG4gIDxBZ2dDaGFydENvbXBvbmVudD48L0FnZ0NoYXJ0Q29tcG9uZW50PlxuICA8aHI+XG4gIDxUYWJsZUNvbXBvbmVudD48L1RhYmxlQ29tcG9uZW50PlxuYFxuIiwiZXhwb3J0IGNvbnN0IG9yZ1RlbXBsYXRlID0gYFxuICA8dWw+XG4gICAge3sjaXRlbV9jb2xsZWN0aW9uc319XG4gICAgICA8bGk+XG4gICAgICAgIDxhIGhyZWY9XCJqYXZhc2NyaXB0OnZvaWQoMClcIiBvbi1jbGljaz1cIm5hdmlnYXRlXCI+e3t0aXRsZX19PC9hPlxuICAgICAgPC9saT5cbiAgICB7ey99fVxuICA8L3VsPlxuYFxuIiwiXG5pbXBvcnQge0luZGV4TW9kZWx9IGZyb20gJy4uL21vZGVscy9pbmRleC5qcyc7XG5pbXBvcnQge0luZGV4VGVtcGxhdGV9IGZyb20gJy4uL3RlbXBsYXRlcy9pbmRleC5odG1sLmpzJztcblxuZXhwb3J0IGNvbnN0IEluZGV4VmlldyA9IHtcbiAgcmVuZGVyOiBmdW5jdGlvbigpIHtcbiAgICB0aGlzLmluZGV4TW9kZWwgPSBuZXcgSW5kZXhNb2RlbCgpO1xuICAgIHRoaXMuaW5kZXhNb2RlbC5mZXRjaCgpLnRoZW4oZnVuY3Rpb24oZGF0YSl7XG4gICAgICB0aGlzLnJhY3RpdmUgPSBuZXcgUmFjdGl2ZSh7XG4gICAgICAgIGVsOiAnI21haW4tY29udGVudC1hcmVhJyxcbiAgICAgICAgdGVtcGxhdGU6IEluZGV4VGVtcGxhdGUsXG4gICAgICAgIGRhdGE6IHtcbiAgICAgICAgICBvcmdzOiBkYXRhLm9yZ3NcbiAgICAgICAgfVxuICAgICAgfSk7XG4gICAgICB0aGlzLnJhY3RpdmUub24oJ25hdmlnYXRlJywgZnVuY3Rpb24oZXZlbnQsIG1ldGhvZCl7XG4gICAgICAgIC8vIGNvbnNvbGUubG9nKGV2ZW50LmNvbnRleHQudXJsKTtcbiAgICAgICAgZXZlbnRCdXMudHJpZ2dlcignbmF2aWdhdGUnLCBldmVudC5jb250ZXh0LnVybCk7XG4gICAgICB9KTtcbiAgICB9KVxuICB9XG59XG4iLCJcbmltcG9ydCB7SXRlbUNvbGxlY3Rpb25Nb2RlbH0gZnJvbSAnLi4vbW9kZWxzL2l0ZW1fY29sbGVjdGlvbi5qcyc7XG5pbXBvcnQge1RhYmxlVGVtcGxhdGUsIEFnZ0NoYXJ0VGVtcGxhdGUsIEl0ZW1Db2xsZWN0aW9uVGVtcGxhdGV9IGZyb20gJy4uL3RlbXBsYXRlcy9pdGVtX2NvbGxlY3Rpb24uaHRtbC5qcyc7XG5cbi8vIENvbXBvbmVudHNcbi8vIHRhYmxlXG4vLyBjaGFydFxuXG5sZXQgVGFibGVDb21wb25lbnQgPSBSYWN0aXZlLmV4dGVuZCh7XG4gIGlzb2xhdGVkOiBmYWxzZSxcbiAgdGVtcGxhdGU6IFRhYmxlVGVtcGxhdGVcbn0pO1xuXG5sZXQgQWdnQ2hhcnRDb21wb25lbnQgPSBSYWN0aXZlLmV4dGVuZCh7XG4gIHRlbXBsYXRlOiBBZ2dDaGFydFRlbXBsYXRlLFxuICBvbmNvbXBsZXRlOiBmdW5jdGlvbigpe1xuICAgIGxldCBkYXRlX2l0ZW1fY291bnRzID0gdGhpcy5wYXJlbnQuZ2V0KCdkYXRlX2l0ZW1fY291bnRzJyk7XG4gICAgY29uc3QgaXRlbXMgPSB0aGlzLnBhcmVudC5nZXQoJ2l0ZW1zJyk7XG4gICAgY29uc3QgZGF0ZV9zYWxlcyA9IHRoaXMucGFyZW50LmdldCgnZGF0ZV9zYWxlcycpO1xuICAgIGxldCBkYXRlcyA9IFsneCddO1xuICAgIGxldCBpdGVtX2NvdW50cyA9IHt9XG4gICAgbGV0IGRhdGVfc2FsZXNfY29sdW1uID0gWydkYXRlX3NhbGVzJ11cbiAgICBmb3IgKGxldCBpdGVtX2RhdGUgaW4gZGF0ZV9pdGVtX2NvdW50cykge1xuICAgICAgZGF0ZXMucHVzaChpdGVtX2RhdGUpO1xuICAgICAgZGF0ZV9zYWxlc19jb2x1bW4ucHVzaChkYXRlX3NhbGVzW2l0ZW1fZGF0ZV0pO1xuICAgICAgaXRlbXMuZm9yRWFjaCgoaXRlbSkgPT4ge1xuICAgICAgICBpZiAoIWl0ZW1fY291bnRzW2l0ZW0uaWRdKSB7XG4gICAgICAgICAgaXRlbV9jb3VudHNbaXRlbS5pZF0gPSBbXTtcbiAgICAgICAgfVxuICAgICAgICBpZiAoZGF0ZV9pdGVtX2NvdW50c1tpdGVtX2RhdGVdLmhhc093blByb3BlcnR5KGl0ZW0uaWQpKSB7XG4gICAgICAgICAgLy8gSWYgYW4gaXRlbSBoYXMgYmVlbiBib3VnaHQgb24gdGhpcyBpdGVtX2RhdGVcbiAgICAgICAgICBpdGVtX2NvdW50c1tpdGVtLmlkXS5wdXNoKGRhdGVfaXRlbV9jb3VudHNbaXRlbV9kYXRlXVtpdGVtLmlkXSk7XG4gICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgLy8gSXRlbSBub3QgYm91Z2h0IG9uIHRoaXMgZGF0ZVxuICAgICAgICAgIGl0ZW1fY291bnRzW2l0ZW0uaWRdLnB1c2goMCk7XG4gICAgICAgIH1cbiAgICAgIH0pXG4gICAgfVxuXG4gICAgbGV0IGNvbHVtbnMgPSBbZGF0ZXNdO1xuICAgIGl0ZW1zLmZvckVhY2goKGl0ZW0pID0+e1xuICAgICAgY29sdW1ucy5wdXNoKFtpdGVtLnRpdGxlXS5jb25jYXQoaXRlbV9jb3VudHNbaXRlbS5pZF0pKTtcbiAgICB9KVxuXG4gICAgbGV0IGJhcl9ncmFwaF9oZWFkZXJzID0gY29sdW1ucy5tYXAoKGNvbCkgPT4gY29sWzBdKS5maWx0ZXIoKGhlYWRlcikgPT4gaGVhZGVyICE9PSAneCcpO1xuXG4gICAgY29sdW1ucy5wdXNoKGRhdGVfc2FsZXNfY29sdW1uKTtcblxuICAgIHRoaXMuY2hhcnQgPSBjMy5nZW5lcmF0ZSh7XG4gICAgICBkYXRhOiB7XG4gICAgICAgIHg6ICd4JyxcbiAgICAgICAgY29sdW1uczogY29sdW1ucyxcbiAgICAgICAgdHlwZTogJ2JhcicsXG4gICAgICAgIHR5cGVzOiB7XG4gICAgICAgICAgZGF0ZV9zYWxlczogJ2xpbmUnXG4gICAgICAgIH0sXG4gICAgICAgIGdyb3VwczogW1xuICAgICAgICAgIGJhcl9ncmFwaF9oZWFkZXJzXG4gICAgICAgIF0sXG4gICAgICAgIGF4ZXM6IHtcbiAgICAgICAgICBkYXRlX3NhbGVzOiAneTInXG4gICAgICAgIH1cbiAgICAgIH0sXG4gICAgICBiYXI6IHtcbiAgICAgICAgd2lkdGg6IHtcbiAgICAgICAgICByYXRpbzogMC41IC8vIHRoaXMgbWFrZXMgYmFyIHdpZHRoIDUwJSBvZiBsZW5ndGggYmV0d2VlbiB0aWNrc1xuICAgICAgICB9XG4gICAgICB9LFxuICAgICAgYXhpczoge1xuICAgICAgICB4OiB7XG4gICAgICAgICAgdHlwZTogJ3RpbWVzZXJpZXMnLFxuICAgICAgICAgIHRpY2s6IHtcbiAgICAgICAgICAgIGZvcm1hdDogJyVkLSVtJ1xuICAgICAgICAgIH1cbiAgICAgICAgfSxcbiAgICAgICAgeTI6IHtcbiAgICAgICAgICBzaG93OiB0cnVlXG4gICAgICAgIH1cbiAgICAgIH1cbiAgICB9KTtcbiAgfVxufSlcblxuZXhwb3J0IGNvbnN0IEl0ZW1Db2xsZWN0aW9uVmlldyA9IHtcbiAgaW5pdDogZnVuY3Rpb24oZGF0YSl7XG4gICAgdGhpcy5yYWN0aXZlID0gbmV3IFJhY3RpdmUoe1xuICAgICAgZWw6ICcjbWFpbi1jb250ZW50LWFyZWEnLFxuICAgICAgdGVtcGxhdGU6IEl0ZW1Db2xsZWN0aW9uVGVtcGxhdGUsXG4gICAgICBkYXRhOiB7XG4gICAgICAgIGl0ZW1zOiB0aGlzLm1vZGVsLmdldCgnaXRlbXMnKSxcbiAgICAgICAgZGF0ZV9pdGVtX2NvdW50czogdGhpcy5tb2RlbC5nZXQoJ2RhdGVfaXRlbV9jb3VudHMnKSxcbiAgICAgICAgZGF0ZV9zYWxlczogdGhpcy5tb2RlbC5nZXQoJ2RhdGVfc2FsZXMnKSxcbiAgICAgICAgbmV0X3NhbGVzOiB0aGlzLm1vZGVsLmdldCgnbmV0X3NhbGVzJylcbiAgICAgIH0sXG4gICAgICBjb21wb25lbnRzOiB7VGFibGVDb21wb25lbnQ6IFRhYmxlQ29tcG9uZW50LCBBZ2dDaGFydENvbXBvbmVudDogQWdnQ2hhcnRDb21wb25lbnR9XG4gICAgfSk7XG5cbiAgICB0aGlzLm1vZGVsLm9uKCdjaGFuZ2U6aXRlbXMnLCAobW9kZWwsIGl0ZW1zKSA9PiB0aGlzLnJhY3RpdmUuc2V0KCdpdGVtcycsIGl0ZW1zKSk7XG5cbiAgICB0aGlzLnJhY3RpdmUub24oJ25hdmlnYXRlJywgZnVuY3Rpb24oZXZlbnQsIG1ldGhvZCl7XG4gICAgICAvLyBraWxsIGludGVydmFsXG4gICAgICBjbGVhckludGVydmFsKHRoaXMuaW50ZXJ2YWxJZCk7XG4gICAgICBldmVudEJ1cy50cmlnZ2VyKCduYXZpZ2F0ZScsIGV2ZW50LmNvbnRleHQudXJsKTtcbiAgICB9KTtcbiAgICB3aW5kb3cuYWRkRXZlbnRMaXN0ZW5lcigncG9wc3RhdGUnLCAoZXZlbnQpID0+IHtcbiAgICAgIC8vIGtpbGwgaW50ZXJ2YWxcbiAgICAgIGNsZWFySW50ZXJ2YWwodGhpcy5pbnRlcnZhbElkKTtcbiAgICB9KTtcbiAgfSxcbiAgZmV0Y2g6IGZ1bmN0aW9uKCl7XG4gICAgcmV0dXJuIHRoaXMubW9kZWwuZmV0Y2goKS50aGVuKGRhdGEgPT4ge1xuICAgICAgdGhpcy5tb2RlbC5zZXQoJ2l0ZW1zJywgZGF0YS5pdGVtcyk7XG4gICAgICB0aGlzLm1vZGVsLnNldCgnZGF0ZV9pdGVtX2NvdW50cycsIGRhdGEuZGF0ZV9pdGVtX2NvdW50cyk7XG4gICAgICB0aGlzLm1vZGVsLnNldCgnZGF0ZV9zYWxlcycsIGRhdGEuZGF0ZV9zYWxlcyk7XG4gICAgICB0aGlzLm1vZGVsLnNldCgnbmV0X3NhbGVzJywgZGF0YS5uZXRfc2FsZXMpO1xuICAgIH0pO1xuICB9LFxuICByZWZyZXNoOiBmdW5jdGlvbigpe1xuICAgIHRoaXMuZmV0Y2goKTtcbiAgfSxcbiAgcmVuZGVyOiBmdW5jdGlvbihpbml0RGF0YSkge1xuICAgIHRoaXMubW9kZWwgPSBuZXcgSXRlbUNvbGxlY3Rpb25Nb2RlbCh7XG4gICAgICBpZDogaW5pdERhdGEuaWRcbiAgICB9KTtcblxuICAgIHRoaXMuZmV0Y2goKS50aGVuKCgpID0+IHRoaXMuaW5pdCgpKTtcblxuICAgIHRoaXMuaW50ZXJ2YWxJZCA9IHNldEludGVydmFsKCgpID0+IHRoaXMucmVmcmVzaCgpLCAzMDAwKTtcbiAgfVxufVxuIiwiXG5pbXBvcnQge09yZ01vZGVsfSBmcm9tICcuLi9tb2RlbHMvb3JnLmpzJztcbi8vIGltcG9ydCB7cmVuZGVydmlld30gZnJvbSAnLi9yZW5kZXJ2aWV3LmpzJztcbmltcG9ydCB7b3JnVGVtcGxhdGV9IGZyb20gJy4uL3RlbXBsYXRlcy9vcmcuaHRtbC5qcyc7XG5cbmV4cG9ydCBjb25zdCBPcmdWaWV3ID0ge1xuICByZW5kZXI6IGZ1bmN0aW9uKG9yZykge1xuICAgIHRoaXMub3JnTW9kZWwgPSBuZXcgT3JnTW9kZWwoe1xuICAgICAgbmFtZTogb3JnLm5hbWVcbiAgICB9KTtcbiAgICB0aGlzLm9yZ01vZGVsLmZldGNoKCkudGhlbihmdW5jdGlvbihkYXRhKXtcbiAgICAgIHRoaXMucmFjdGl2ZSA9IG5ldyBSYWN0aXZlKHtcbiAgICAgICAgZWw6ICcjbWFpbi1jb250ZW50LWFyZWEnLFxuICAgICAgICAvLyB0ZW1wbGF0ZTogJyNvcmctY29udGVudC10ZW1wbGF0ZScsXG4gICAgICAgIHRlbXBsYXRlOiBvcmdUZW1wbGF0ZSxcbiAgICAgICAgZGF0YToge1xuICAgICAgICAgIG5hbWU6IGRhdGEubmFtZSxcbiAgICAgICAgICBpdGVtX2NvbGxlY3Rpb25zOiBkYXRhLml0ZW1fY29sbGVjdGlvbnNcbiAgICAgICAgfVxuICAgICAgfSk7XG4gICAgICB0aGlzLnJhY3RpdmUub24oJ25hdmlnYXRlJywgZnVuY3Rpb24oZXZlbnQsIG1ldGhvZCl7XG4gICAgICAgIC8vIGNvbnNvbGUubG9nKGV2ZW50LmNvbnRleHQudXJsKTtcbiAgICAgICAgZXZlbnRCdXMudHJpZ2dlcignbmF2aWdhdGUnLCBldmVudC5jb250ZXh0LnVybCk7XG4gICAgICB9KTtcbiAgICB9KTtcblxuICB9XG59XG4iLCJcbmltcG9ydCB7SW5kZXhWaWV3fSBmcm9tICcuL2luZGV4LmpzJztcbmltcG9ydCB7T3JnVmlld30gZnJvbSAnLi9vcmcuanMnO1xuaW1wb3J0IHtJdGVtQ29sbGVjdGlvblZpZXd9IGZyb20gJy4vaXRlbV9jb2xsZWN0aW9uLmpzJztcblxuZXhwb3J0IGNvbnN0IFJvdXRlciA9IEJhY2tib25lLlJvdXRlci5leHRlbmQoe1xuICByb3V0ZXM6IHtcbiAgICBcIlwiOiBcImluZGV4XCIsXG4gICAgXCJvLzpvcmdcIjogXCJvcmdcIixcbiAgICBcImljLzppY0lkXCI6IFwiaXRlbV9jb2xsZWN0aW9uXCJcbiAgfSxcbiAgaW5kZXg6IGZ1bmN0aW9uKCkge1xuICAgIEluZGV4Vmlldy5yZW5kZXIoKTtcbiAgfSxcbiAgb3JnOiBmdW5jdGlvbihvcmcpe1xuICAgIE9yZ1ZpZXcucmVuZGVyKHtuYW1lOiBvcmd9KTtcbiAgfSxcbiAgaXRlbV9jb2xsZWN0aW9uOiBmdW5jdGlvbihpY0lkKXtcbiAgICBJdGVtQ29sbGVjdGlvblZpZXcucmVuZGVyKHtpZDogaWNJZH0pO1xuICB9XG59KTtcbiJdfQ==
