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
    return "/admin";
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
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCIvaG9tZS9zaHJleWFzL2Rldi9oYXNnZWVrL2JveG9mZmljZS9ib3hvZmZpY2Uvc3RhdGljL2pzL3ZpZXdzL21haW4uanMiLCIvaG9tZS9zaHJleWFzL2Rldi9oYXNnZWVrL2JveG9mZmljZS9ib3hvZmZpY2Uvc3RhdGljL2pzL21vZGVscy9pbmRleC5qcyIsIi9ob21lL3NocmV5YXMvZGV2L2hhc2dlZWsvYm94b2ZmaWNlL2JveG9mZmljZS9zdGF0aWMvanMvbW9kZWxzL2l0ZW1fY29sbGVjdGlvbi5qcyIsIi9ob21lL3NocmV5YXMvZGV2L2hhc2dlZWsvYm94b2ZmaWNlL2JveG9mZmljZS9zdGF0aWMvanMvbW9kZWxzL29yZy5qcyIsIi9ob21lL3NocmV5YXMvZGV2L2hhc2dlZWsvYm94b2ZmaWNlL2JveG9mZmljZS9zdGF0aWMvanMvdGVtcGxhdGVzL2luZGV4Lmh0bWwuanMiLCIvaG9tZS9zaHJleWFzL2Rldi9oYXNnZWVrL2JveG9mZmljZS9ib3hvZmZpY2Uvc3RhdGljL2pzL3RlbXBsYXRlcy9pdGVtX2NvbGxlY3Rpb24uaHRtbC5qcyIsIi9ob21lL3NocmV5YXMvZGV2L2hhc2dlZWsvYm94b2ZmaWNlL2JveG9mZmljZS9zdGF0aWMvanMvdGVtcGxhdGVzL29yZy5odG1sLmpzIiwiL2hvbWUvc2hyZXlhcy9kZXYvaGFzZ2Vlay9ib3hvZmZpY2UvYm94b2ZmaWNlL3N0YXRpYy9qcy92aWV3cy9pbmRleC5qcyIsIi9ob21lL3NocmV5YXMvZGV2L2hhc2dlZWsvYm94b2ZmaWNlL2JveG9mZmljZS9zdGF0aWMvanMvdmlld3MvaXRlbV9jb2xsZWN0aW9uLmpzIiwiL2hvbWUvc2hyZXlhcy9kZXYvaGFzZ2Vlay9ib3hvZmZpY2UvYm94b2ZmaWNlL3N0YXRpYy9qcy92aWV3cy9vcmcuanMiLCIvaG9tZS9zaHJleWFzL2Rldi9oYXNnZWVrL2JveG9mZmljZS9ib3hvZmZpY2Uvc3RhdGlj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R0FDOUI7QUFDRCxPQUFLLEVBQUUsaUJBQVc7QUFDaEIsYUFBUyxDQUFDLE1BQU0sRUFBRSxDQUFDO0dBQ3BCO0FBQ0QsS0FBRzs7Ozs7Ozs7OztLQUFFLFVBQVMsR0FBRyxFQUFDO0FBQ2hCLFdBQU8sQ0FBQyxNQUFNLENBQUMsRUFBQyxJQUFJLEVBQUUsR0FBRyxFQUFDLENBQUMsQ0FBQztHQUM3QixDQUFBO0FBQ0QsaUJBQWUsRUFBRSx5QkFBUyxJQUFJLEVBQUM7QUFDN0Isc0JBQWtCLENBQUMsTUFBTSxDQUFDLEVBQUMsRUFBRSxFQUFFLElBQUksRUFBQyxDQUFDLENBQUM7R0FDdkM7Q0FDRixDQUFDLENBQUM7UUFmVSxNQUFNLEdBQU4sTUFBTSIsImZpbGUiOiJnZW5lcmF0ZWQuanMiLCJzb3VyY2VSb290IjoiIiwic291cmNlc0NvbnRlbnQiOlsiKGZ1bmN0aW9uIGUodCxuLHIpe2Z1bmN0aW9uIHMobyx1KXtpZighbltvXSl7aWYoIXRbb10pe3ZhciBhPXR5cGVvZiByZXF1aXJlPT1cImZ1bmN0aW9uXCImJnJlcXVpcmU7aWYoIXUmJmEpcmV0dXJuIGEobywhMCk7aWYoaSlyZXR1cm4gaShvLCEwKTt2YXIgZj1uZXcgRXJyb3IoXCJDYW5ub3QgZmluZCBtb2R1bGUgJ1wiK28rXCInXCIpO3Rocm93IGYuY29kZT1cIk1PRFVMRV9OT1RfRk9VTkRcIixmfXZhciBsPW5bb109e2V4cG9ydHM6e319O3Rbb11bMF0uY2FsbChsLmV4cG9ydHMsZnVuY3Rpb24oZSl7dmFyIG49dFtvXVsxXVtlXTtyZXR1cm4gcyhuP246ZSl9LGwsbC5leHBvcnRzLGUsdCxuLHIpfXJldHVybiBuW29dLmV4cG9ydHN9dmFyIGk9dHlwZW9mIHJlcXVpcmU9PVwiZnVuY3Rpb25cIiYmcmVxdWlyZTtmb3IodmFyIG89MDtvPHIubGVuZ3RoO28rKylzKHJbb10pO3JldHVybiBzfSkiLCJcbmltcG9ydCB7Um91dGVyfSBmcm9tICcuL3JvdXRlcic7XG5cblxuJChmdW5jdGlvbigpe1xuICBsZXQgYXBwUm91dGVyID0gbmV3IFJvdXRlcigpO1xuICBCYWNrYm9uZS5oaXN0b3J5LnN0YXJ0KHtwdXNoU3RhdGU6IHRydWUsIHJvb3Q6IFwiL2FkbWluL1wifSk7XG4gIHdpbmRvdy5ldmVudEJ1cyA9IF8uY2xvbmUoQmFja2JvbmUuRXZlbnRzKTtcbiAgd2luZG93LmV2ZW50QnVzLm9uKCduYXZpZ2F0ZScsIGZ1bmN0aW9uKG1zZyl7XG4gICAgYXBwUm91dGVyLm5hdmlnYXRlKG1zZywge3RyaWdnZXI6IHRydWV9KTtcbiAgfSlcbn0pO1xuXG4iLCJcbmV4cG9ydCBjb25zdCBJbmRleE1vZGVsID0gQmFja2JvbmUuTW9kZWwuZXh0ZW5kKHtcbiAgdXJsIDogZnVuY3Rpb24oKXtcbiAgICByZXR1cm4gJy9hZG1pbic7XG4gIH1cbn0pO1xuIiwiXG5leHBvcnQgY29uc3QgSXRlbUNvbGxlY3Rpb25Nb2RlbCA9IEJhY2tib25lLk1vZGVsLmV4dGVuZCh7XG4gIHVybCA6IGZ1bmN0aW9uKGlkKXtcbiAgICByZXR1cm4gJy9hZG1pbi9pYy8nICsgdGhpcy5nZXQoJ2lkJyk7XG4gIH1cbn0pO1xuIiwiXG5leHBvcnQgY29uc3QgT3JnTW9kZWwgPSBCYWNrYm9uZS5Nb2RlbC5leHRlbmQoe1xuICB1cmwgOiBmdW5jdGlvbihuYW1lKXtcbiAgICByZXR1cm4gJy9hZG1pbi9vLycgKyB0aGlzLmdldCgnbmFtZScpO1xuICB9XG59KTtcbiIsImV4cG9ydCBjb25zdCBJbmRleFRlbXBsYXRlID0gYFxuICB7eyNvcmdzfX1cbiAgICA8YSBocmVmPVwiamF2YXNjcmlwdDp2b2lkKDApXCIgb24tY2xpY2s9XCJuYXZpZ2F0ZVwiPnt7dGl0bGV9fTwvYT5cbiAge3svfX1cbmBcbiIsImV4cG9ydCBjb25zdCBUYWJsZVRlbXBsYXRlID0gYFxuICA8ZGl2IGNsYXNzPVwidGFibGUtcmVzcG9uc2l2ZSBzdGF0c1wiPlxuICAgIDx0YWJsZSBjbGFzcz1cInRhYmxlIHRhYmxlLWJvcmRlcmVkIHRhYmxlLWhvdmVyIHN0YXRzLXRhYmxlXCI+XG4gICAgICA8dGhlYWQ+XG4gICAgICAgIDx0ciBjbGFzcz1cImluZm9cIj5cbiAgICAgICAgICA8dGg+IzwvdGg+XG4gICAgICAgICAgPHRoPkl0ZW08L3RoPlxuICAgICAgICAgIDx0aD5BdmFpbGFibGU8L3RoPlxuICAgICAgICAgIDx0aD5Tb2xkPC90aD5cbiAgICAgICAgICA8dGg+RnJlZTwvdGg+XG4gICAgICAgICAgPHRoPkNhbmNlbGxlZDwvdGg+XG4gICAgICAgICAgPHRoPkN1cnJlbnQgUHJpY2U8L3RoPlxuICAgICAgICAgIDx0aD5OZXQgU2FsZXM8L3RoPlxuICAgICAgICA8L3RyPlxuICAgICAgPC90aGVhZD5cbiAgICAgIDx0Ym9keT5cbiAgICAgICAge3sjaXRlbXN9fVxuICAgICAgICAgIDx0cj5cbiAgICAgICAgICAgIDx0ZD57eyBAaW5kZXggKyAxIH19PC90ZD5cbiAgICAgICAgICAgIDx0ZD57eyB0aXRsZSB9fTwvdGQ+XG4gICAgICAgICAgICA8dGQ+e3sgYXZhaWxhYmxlIH19PC90ZD5cbiAgICAgICAgICAgIDx0ZD57eyBzb2xkIH19PC90ZD5cbiAgICAgICAgICAgIDx0ZD57eyBmcmVlIH19PC90ZD5cbiAgICAgICAgICAgIDx0ZD57eyBjYW5jZWxsZWQgfX08L3RkPlxuICAgICAgICAgICAgPHRkPnt7IGN1cnJlbnRfcHJpY2UgfX08L3RkPlxuICAgICAgICAgICAgPHRkPnt7IG5ldF9zYWxlcyB9fTwvdGQ+XG4gICAgICAgICAgPC90cj5cbiAgICAgICAge3svfX1cbiAgICAgIDwvdGJvZHk+XG4gICAgPC90YWJsZT5cbiAgPC9kaXY+XG5gXG5cbmV4cG9ydCBjb25zdCBBZ2dDaGFydFRlbXBsYXRlID0gYFxuICA8ZGl2IGlkPVwiY2hhcnRcIiBjbGFzcz1cImMzXCIgc3R5bGU9XCJtYXgtaGVpZ2h0OiAyODBweDsgcG9zaXRpb246IHJlbGF0aXZlO1wiPlxuICA8L2Rpdj5cbmBcblxuZXhwb3J0IGNvbnN0IEl0ZW1Db2xsZWN0aW9uVGVtcGxhdGUgPSBgXG4gIDxicj5cbiAgPGRpdiBjbGFzcz1cInJvd1wiPlxuICAgIDxkaXYgY2xhc3M9XCJjb2wtbWQtNFwiPlxuICAgICAgPGRpdiBjbGFzcz1cInBhbmVsIHBhbmVsLWRlZmF1bHRcIj5cbiAgICAgICAgPGRpdiBjbGFzcz1cInBhbmVsLWhlYWRpbmdcIj5cbiAgICAgICAgICA8aDMgY2xhc3M9XCJwYW5lbC10aXRsZVwiPk5ldCBTYWxlczwvaDM+XG4gICAgICAgIDwvZGl2PlxuICAgICAgICA8ZGl2IGNsYXNzPVwicGFuZWwtYm9keVwiPlxuICAgICAgICAgIHt7bmV0X3NhbGVzfX1cbiAgICAgICAgPC9kaXY+XG4gICAgICA8L2Rpdj5cbiAgICA8L2Rpdj5cbiAgPC9kaXY+XG4gIDxocj5cbiAgPEFnZ0NoYXJ0Q29tcG9uZW50PjwvQWdnQ2hhcnRDb21wb25lbnQ+XG4gIDxocj5cbiAgPFRhYmxlQ29tcG9uZW50PjwvVGFibGVDb21wb25lbnQ+XG5gXG4iLCJleHBvcnQgY29uc3Qgb3JnVGVtcGxhdGUgPSBgXG4gIDx1bD5cbiAgICB7eyNpdGVtX2NvbGxlY3Rpb25zfX1cbiAgICAgIDxsaT5cbiAgICAgICAgPGEgaHJlZj1cImphdmFzY3JpcHQ6dm9pZCgwKVwiIG9uLWNsaWNrPVwibmF2aWdhdGVcIj57e3RpdGxlfX08L2E+XG4gICAgICA8L2xpPlxuICAgIHt7L319XG4gIDwvdWw+XG5gXG4iLCJcbmltcG9ydCB7SW5kZXhNb2RlbH0gZnJvbSAnLi4vbW9kZWxzL2luZGV4LmpzJztcbmltcG9ydCB7SW5kZXhUZW1wbGF0ZX0gZnJvbSAnLi4vdGVtcGxhdGVzL2luZGV4Lmh0bWwuanMnO1xuXG5leHBvcnQgY29uc3QgSW5kZXhWaWV3ID0ge1xuICByZW5kZXI6IGZ1bmN0aW9uKCkge1xuICAgIHRoaXMuaW5kZXhNb2RlbCA9IG5ldyBJbmRleE1vZGVsKCk7XG4gICAgdGhpcy5pbmRleE1vZGVsLmZldGNoKCkudGhlbihmdW5jdGlvbihkYXRhKXtcbiAgICAgIHRoaXMucmFjdGl2ZSA9IG5ldyBSYWN0aXZlKHtcbiAgICAgICAgZWw6ICcjbWFpbi1jb250ZW50LWFyZWEnLFxuICAgICAgICB0ZW1wbGF0ZTogSW5kZXhUZW1wbGF0ZSxcbiAgICAgICAgZGF0YToge1xuICAgICAgICAgIG9yZ3M6IGRhdGEub3Jnc1xuICAgICAgICB9XG4gICAgICB9KTtcbiAgICAgIHRoaXMucmFjdGl2ZS5vbignbmF2aWdhdGUnLCBmdW5jdGlvbihldmVudCwgbWV0aG9kKXtcbiAgICAgICAgZXZlbnRCdXMudHJpZ2dlcignbmF2aWdhdGUnLCBldmVudC5jb250ZXh0LnVybCk7XG4gICAgICB9KTtcbiAgICB9KVxuICB9XG59XG4iLCJcbmltcG9ydCB7SXRlbUNvbGxlY3Rpb25Nb2RlbH0gZnJvbSAnLi4vbW9kZWxzL2l0ZW1fY29sbGVjdGlvbi5qcyc7XG5pbXBvcnQge1RhYmxlVGVtcGxhdGUsIEFnZ0NoYXJ0VGVtcGxhdGUsIEl0ZW1Db2xsZWN0aW9uVGVtcGxhdGV9IGZyb20gJy4uL3RlbXBsYXRlcy9pdGVtX2NvbGxlY3Rpb24uaHRtbC5qcyc7XG5cbi8vIENvbXBvbmVudHNcbi8vIHRhYmxlXG4vLyBjaGFydFxuXG5sZXQgVGFibGVDb21wb25lbnQgPSBSYWN0aXZlLmV4dGVuZCh7XG4gIGlzb2xhdGVkOiBmYWxzZSxcbiAgdGVtcGxhdGU6IFRhYmxlVGVtcGxhdGVcbn0pO1xuXG5sZXQgQWdnQ2hhcnRDb21wb25lbnQgPSBSYWN0aXZlLmV4dGVuZCh7XG4gIHRlbXBsYXRlOiBBZ2dDaGFydFRlbXBsYXRlLFxuICBvbmNvbXBsZXRlOiBmdW5jdGlvbigpe1xuICAgIGxldCBkYXRlX2l0ZW1fY291bnRzID0gdGhpcy5wYXJlbnQuZ2V0KCdkYXRlX2l0ZW1fY291bnRzJyk7XG4gICAgY29uc3QgaXRlbXMgPSB0aGlzLnBhcmVudC5nZXQoJ2l0ZW1zJyk7XG4gICAgY29uc3QgZGF0ZV9zYWxlcyA9IHRoaXMucGFyZW50LmdldCgnZGF0ZV9zYWxlcycpO1xuICAgIGxldCBkYXRlcyA9IFsneCddO1xuICAgIGxldCBpdGVtX2NvdW50cyA9IHt9XG4gICAgbGV0IGRhdGVfc2FsZXNfY29sdW1uID0gWydkYXRlX3NhbGVzJ11cbiAgICBmb3IgKGxldCBpdGVtX2RhdGUgaW4gZGF0ZV9pdGVtX2NvdW50cykge1xuICAgICAgZGF0ZXMucHVzaChpdGVtX2RhdGUpO1xuICAgICAgZGF0ZV9zYWxlc19jb2x1bW4ucHVzaChkYXRlX3NhbGVzW2l0ZW1fZGF0ZV0pO1xuICAgICAgaXRlbXMuZm9yRWFjaCgoaXRlbSkgPT4ge1xuICAgICAgICBpZiAoIWl0ZW1fY291bnRzW2l0ZW0uaWRdKSB7XG4gICAgICAgICAgaXRlbV9jb3VudHNbaXRlbS5pZF0gPSBbXTtcbiAgICAgICAgfVxuICAgICAgICBpZiAoZGF0ZV9pdGVtX2NvdW50c1tpdGVtX2RhdGVdLmhhc093blByb3BlcnR5KGl0ZW0uaWQpKSB7XG4gICAgICAgICAgLy8gSWYgYW4gaXRlbSBoYXMgYmVlbiBib3VnaHQgb24gdGhpcyBpdGVtX2RhdGVcbiAgICAgICAgICBpdGVtX2NvdW50c1tpdGVtLmlkXS5wdXNoKGRhdGVfaXRlbV9jb3VudHNbaXRlbV9kYXRlXVtpdGVtLmlkXSk7XG4gICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgLy8gSXRlbSBub3QgYm91Z2h0IG9uIHRoaXMgZGF0ZVxuICAgICAgICAgIGl0ZW1fY291bnRzW2l0ZW0uaWRdLnB1c2goMCk7XG4gICAgICAgIH1cbiAgICAgIH0pXG4gICAgfVxuXG4gICAgbGV0IGNvbHVtbnMgPSBbZGF0ZXNdO1xuICAgIGl0ZW1zLmZvckVhY2goKGl0ZW0pID0+e1xuICAgICAgY29sdW1ucy5wdXNoKFtpdGVtLnRpdGxlXS5jb25jYXQoaXRlbV9jb3VudHNbaXRlbS5pZF0pKTtcbiAgICB9KVxuXG4gICAgbGV0IGJhcl9ncmFwaF9oZWFkZXJzID0gY29sdW1ucy5tYXAoKGNvbCkgPT4gY29sWzBdKS5maWx0ZXIoKGhlYWRlcikgPT4gaGVhZGVyICE9PSAneCcpO1xuXG4gICAgY29sdW1ucy5wdXNoKGRhdGVfc2FsZXNfY29sdW1uKTtcblxuICAgIHRoaXMuY2hhcnQgPSBjMy5nZW5lcmF0ZSh7XG4gICAgICBkYXRhOiB7XG4gICAgICAgIHg6ICd4JyxcbiAgICAgICAgY29sdW1uczogY29sdW1ucyxcbiAgICAgICAgdHlwZTogJ2JhcicsXG4gICAgICAgIHR5cGVzOiB7XG4gICAgICAgICAgZGF0ZV9zYWxlczogJ2xpbmUnXG4gICAgICAgIH0sXG4gICAgICAgIGdyb3VwczogW1xuICAgICAgICAgIGJhcl9ncmFwaF9oZWFkZXJzXG4gICAgICAgIF0sXG4gICAgICAgIGF4ZXM6IHtcbiAgICAgICAgICBkYXRlX3NhbGVzOiAneTInXG4gICAgICAgIH1cbiAgICAgIH0sXG4gICAgICBiYXI6IHtcbiAgICAgICAgd2lkdGg6IHtcbiAgICAgICAgICByYXRpbzogMC41IC8vIHRoaXMgbWFrZXMgYmFyIHdpZHRoIDUwJSBvZiBsZW5ndGggYmV0d2VlbiB0aWNrc1xuICAgICAgICB9XG4gICAgICB9LFxuICAgICAgYXhpczoge1xuICAgICAgICB4OiB7XG4gICAgICAgICAgdHlwZTogJ3RpbWVzZXJpZXMnLFxuICAgICAgICAgIHRpY2s6IHtcbiAgICAgICAgICAgIGZvcm1hdDogJyVkLSVtJ1xuICAgICAgICAgIH1cbiAgICAgICAgfSxcbiAgICAgICAgeTI6IHtcbiAgICAgICAgICBzaG93OiB0cnVlXG4gICAgICAgIH1cbiAgICAgIH1cbiAgICB9KTtcbiAgfVxufSlcblxuZXhwb3J0IGNvbnN0IEl0ZW1Db2xsZWN0aW9uVmlldyA9IHtcbiAgaW5pdDogZnVuY3Rpb24oZGF0YSl7XG4gICAgdGhpcy5yYWN0aXZlID0gbmV3IFJhY3RpdmUoe1xuICAgICAgZWw6ICcjbWFpbi1jb250ZW50LWFyZWEnLFxuICAgICAgdGVtcGxhdGU6IEl0ZW1Db2xsZWN0aW9uVGVtcGxhdGUsXG4gICAgICBkYXRhOiB7XG4gICAgICAgIGl0ZW1zOiB0aGlzLm1vZGVsLmdldCgnaXRlbXMnKSxcbiAgICAgICAgZGF0ZV9pdGVtX2NvdW50czogdGhpcy5tb2RlbC5nZXQoJ2RhdGVfaXRlbV9jb3VudHMnKSxcbiAgICAgICAgZGF0ZV9zYWxlczogdGhpcy5tb2RlbC5nZXQoJ2RhdGVfc2FsZXMnKSxcbiAgICAgICAgbmV0X3NhbGVzOiB0aGlzLm1vZGVsLmdldCgnbmV0X3NhbGVzJylcbiAgICAgIH0sXG4gICAgICBjb21wb25lbnRzOiB7VGFibGVDb21wb25lbnQ6IFRhYmxlQ29tcG9uZW50LCBBZ2dDaGFydENvbXBvbmVudDogQWdnQ2hhcnRDb21wb25lbnR9XG4gICAgfSk7XG5cbiAgICB0aGlzLm1vZGVsLm9uKCdjaGFuZ2U6aXRlbXMnLCAobW9kZWwsIGl0ZW1zKSA9PiB0aGlzLnJhY3RpdmUuc2V0KCdpdGVtcycsIGl0ZW1zKSk7XG5cbiAgICB0aGlzLnJhY3RpdmUub24oJ25hdmlnYXRlJywgZnVuY3Rpb24oZXZlbnQsIG1ldGhvZCl7XG4gICAgICAvLyBraWxsIGludGVydmFsXG4gICAgICBjbGVhckludGVydmFsKHRoaXMuaW50ZXJ2YWxJZCk7XG4gICAgICBldmVudEJ1cy50cmlnZ2VyKCduYXZpZ2F0ZScsIGV2ZW50LmNvbnRleHQudXJsKTtcbiAgICB9KTtcbiAgICB3aW5kb3cuYWRkRXZlbnRMaXN0ZW5lcigncG9wc3RhdGUnLCAoZXZlbnQpID0+IHtcbiAgICAgIC8vIGtpbGwgaW50ZXJ2YWxcbiAgICAgIGNsZWFySW50ZXJ2YWwodGhpcy5pbnRlcnZhbElkKTtcbiAgICB9KTtcbiAgfSxcbiAgZmV0Y2g6IGZ1bmN0aW9uKCl7XG4gICAgcmV0dXJuIHRoaXMubW9kZWwuZmV0Y2goKS50aGVuKGRhdGEgPT4ge1xuICAgICAgdGhpcy5tb2RlbC5zZXQoJ2l0ZW1zJywgZGF0YS5pdGVtcyk7XG4gICAgICB0aGlzLm1vZGVsLnNldCgnZGF0ZV9pdGVtX2NvdW50cycsIGRhdGEuZGF0ZV9pdGVtX2NvdW50cyk7XG4gICAgICB0aGlzLm1vZGVsLnNldCgnZGF0ZV9zYWxlcycsIGRhdGEuZGF0ZV9zYWxlcyk7XG4gICAgICB0aGlzLm1vZGVsLnNldCgnbmV0X3NhbGVzJywgZGF0YS5uZXRfc2FsZXMpO1xuICAgIH0pO1xuICB9LFxuICByZWZyZXNoOiBmdW5jdGlvbigpe1xuICAgIHRoaXMuZmV0Y2goKTtcbiAgfSxcbiAgcmVuZGVyOiBmdW5jdGlvbihpbml0RGF0YSkge1xuICAgIHRoaXMubW9kZWwgPSBuZXcgSXRlbUNvbGxlY3Rpb25Nb2RlbCh7XG4gICAgICBpZDogaW5pdERhdGEuaWRcbiAgICB9KTtcblxuICAgIHRoaXMuZmV0Y2goKS50aGVuKCgpID0+IHRoaXMuaW5pdCgpKTtcblxuICAgIHRoaXMuaW50ZXJ2YWxJZCA9IHNldEludGVydmFsKCgpID0+IHRoaXMucmVmcmVzaCgpLCAzMDAwKTtcbiAgfVxufVxuIiwiXG5pbXBvcnQge09yZ01vZGVsfSBmcm9tICcuLi9tb2RlbHMvb3JnLmpzJztcbi8vIGltcG9ydCB7cmVuZGVydmlld30gZnJvbSAnLi9yZW5kZXJ2aWV3LmpzJztcbmltcG9ydCB7b3JnVGVtcGxhdGV9IGZyb20gJy4uL3RlbXBsYXRlcy9vcmcuaHRtbC5qcyc7XG5cbmV4cG9ydCBjb25zdCBPcmdWaWV3ID0ge1xuICByZW5kZXI6IGZ1bmN0aW9uKG9yZykge1xuICAgIHRoaXMub3JnTW9kZWwgPSBuZXcgT3JnTW9kZWwoe1xuICAgICAgbmFtZTogb3JnLm5hbWVcbiAgICB9KTtcbiAgICB0aGlzLm9yZ01vZGVsLmZldGNoKCkudGhlbihmdW5jdGlvbihkYXRhKXtcbiAgICAgIHRoaXMucmFjdGl2ZSA9IG5ldyBSYWN0aXZlKHtcbiAgICAgICAgZWw6ICcjbWFpbi1jb250ZW50LWFyZWEnLFxuICAgICAgICAvLyB0ZW1wbGF0ZTogJyNvcmctY29udGVudC10ZW1wbGF0ZScsXG4gICAgICAgIHRlbXBsYXRlOiBvcmdUZW1wbGF0ZSxcbiAgICAgICAgZGF0YToge1xuICAgICAgICAgIG5hbWU6IGRhdGEubmFtZSxcbiAgICAgICAgICBpdGVtX2NvbGxlY3Rpb25zOiBkYXRhLml0ZW1fY29sbGVjdGlvbnNcbiAgICAgICAgfVxuICAgICAgfSk7XG4gICAgICB0aGlzLnJhY3RpdmUub24oJ25hdmlnYXRlJywgZnVuY3Rpb24oZXZlbnQsIG1ldGhvZCl7XG4gICAgICAgIGV2ZW50QnVzLnRyaWdnZXIoJ25hdmlnYXRlJywgZXZlbnQuY29udGV4dC51cmwpO1xuICAgICAgfSk7XG4gICAgfSk7XG5cbiAgfVxufVxuIiwiXG5pbXBvcnQge0luZGV4Vmlld30gZnJvbSAnLi9pbmRleC5qcyc7XG5pbXBvcnQge09yZ1ZpZXd9IGZyb20gJy4vb3JnLmpzJztcbmltcG9ydCB7SXRlbUNvbGxlY3Rpb25WaWV3fSBmcm9tICcuL2l0ZW1fY29sbGVjdGlvbi5qcyc7XG5cbmV4cG9ydCBjb25zdCBSb3V0ZXIgPSBCYWNrYm9uZS5Sb3V0ZXIuZXh0ZW5kKHtcbiAgcm91dGVzOiB7XG4gICAgXCJcIjogXCJpbmRleFwiLFxuICAgIFwiby86b3JnXCI6IFwib3JnXCIsXG4gICAgXCJpYy86aWNJZFwiOiBcIml0ZW1fY29sbGVjdGlvblwiXG4gIH0sXG4gIGluZGV4OiBmdW5jdGlvbigpIHtcbiAgICBJbmRleFZpZXcucmVuZGVyKCk7XG4gIH0sXG4gIG9yZzogZnVuY3Rpb24ob3JnKXtcbiAgICBPcmdWaWV3LnJlbmRlcih7bmFtZTogb3JnfSk7XG4gIH0sXG4gIGl0ZW1fY29sbGVjdGlvbjogZnVuY3Rpb24oaWNJZCl7XG4gICAgSXRlbUNvbGxlY3Rpb25WaWV3LnJlbmRlcih7aWQ6IGljSWR9KTtcbiAgfVxufSk7XG4iXX0=
