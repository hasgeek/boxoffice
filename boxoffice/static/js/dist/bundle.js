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
var TableTemplate = "\n  <div class=\"table-responsive stats\">\n    <table class=\"table table-bordered table-hover stats-table\">\n      <thead>\n        <tr class=\"info\">\n          <th>#</th>\n          <th>Item</th>\n          <th>Available</th>\n          <th>Sold</th>\n          <th>Free</th>\n          <th>Cancelled</th>\n        </tr>\n      </thead>\n      <tbody>\n        {{#items}}\n          <tr>\n            <td>{{ @index + 1 }}</td>\n            <td>{{ title }}</td>\n            <td>{{ available }}</td>\n            <td>{{ sold }}</td>\n            <td>{{ free }}</td>\n            <td>{{ cancelled }}</td>\n          </tr>\n        {{/}}\n      </tbody>\n    </table>\n  </div>\n";

exports.TableTemplate = TableTemplate;
var ItemCollectionTemplate = "\n  <TableComponent></TableComponent>\n";
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
    console.log(!this.ractive);
    if (!this.indexModel) {
      this.indexModel = new IndexModel();
    }
    this.indexModel.fetch().then(function (data) {
      if (!this.ractive) {
        console.log("ractive");
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
      } else {
        this.ractive.render();
      }
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
var ItemCollectionTemplate = _templatesItem_collectionHtmlJs.ItemCollectionTemplate;

// Components
// table
// chart

var TableComponent = Ractive.extend({
  isolated: false,
  template: TableTemplate
});

var ItemCollectionView = {
  init: function init(data) {
    var _this = this;

    this.ractive = new Ractive({
      el: "#main-content-area",
      template: ItemCollectionTemplate,
      data: {
        items: this.model.get("items")
      },
      components: { TableComponent: TableComponent }
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
  refresh: function refresh() {
    var _this = this;

    this.model.fetch().then(function (data) {
      return _this.model.set("items", data.items);
    });
  },
  render: function render(initData) {
    var _this = this;

    this.model = new ItemCollectionModel({
      id: initData.id
    });

    this.model.fetch().then(function (data) {
      _this.model.set("items", data.items);
      _this.init();
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
    if (!this.orgModel) {
      this.orgModel = new OrgModel({
        name: org.name
      });
    }
    this.orgModel.fetch().then(function (data) {
      if (!this.ractive) {
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
      } else {
        this.ractive.render();
      }
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
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCIvaG9tZS9zaHJleWFzL2Rldi9oYXNnZWVrL2JveG9mZmljZS9ib3hvZmZpY2Uvc3RhdGljL2pzL3ZpZXdzL21haW4uanMiLCIvaG9tZS9zaHJleWFzL2Rldi9oYXNnZWVrL2JveG9mZmljZS9ib3hvZmZpY2Uvc3RhdGljL2pzL21vZGVscy9pbmRleC5qcyIsIi9ob21lL3NocmV5YXMvZGV2L2hhc2dlZWsvYm94b2ZmaWNlL2JveG9mZmljZS9zdGF0aWMvanMvbW9kZWxzL2l0ZW1fY29sbGVjdGlvbi5qcyIsIi9ob21lL3NocmV5YXMvZGV2L2hhc2dlZWsvYm94b2ZmaWNlL2JveG9mZmljZS9zdGF0aWMvanMvbW9kZWxzL29yZy5qcyIsIi9ob21lL3NocmV5YXMvZGV2L2hhc2dlZWsvYm94b2ZmaWNlL2JveG9mZmljZS9zdGF0aWMvanMvdGVtcGxhdGVzL2luZGV4Lmh0bWwuanMiLCIvaG9tZS9zaHJleWFzL2Rldi9oYXNnZWVrL2JveG9mZmljZS9ib3hvZmZpY2Uvc3RhdGljL2pzL3RlbXBsYXRlcy9pdGVtX2NvbGxlY3Rpb24uaHRtbC5qcyIsIi9ob21lL3NocmV5YXMvZGV2L2hhc2dlZWsvYm94b2ZmaWNlL2JveG9mZmljZS9zdGF0aWMvanMvdGVtcGxhdGVzL29yZy5odG1sLmpzIiwiL2hvbWUvc2hyZXlhcy9kZXYvaGFzZ2Vlay9ib3hvZmZpY2UvYm94b2ZmaWNlL3N0YXRpYy9qcy92aWV3cy9pbmRleC5qcyIsIi9ob21lL3NocmV5YXMvZGV2L2hhc2dlZWsvYm94b2ZmaWNlL2JveG9mZmljZS9zdGF0aWMvanMvdmlld3MvaXRlbV9jb2xsZWN0aW9uLmpzIiwiL2hvbWUvc2hyZXlhcy9kZXYvaGFzZ2Vlay9ib3hvZmZpY2UvYm94b2ZmaWNlL3N0YXRpYy9qcy92aWV3cy9vcmcuanMiLCIvaG9tZS9zaHJleWFzL2Rldi9oYXNnZWVrL2JveG9mZmljZS9ib3hvZmZpY2Uvc3RhdGlj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QixFQUEvQyxrQkFBa0I7O0FBRW5CLElBQU0sTUFBTSxHQUFHLFFBQVEsQ0FBQyxNQUFNLENBQUMsTUFBTSxDQUFDO0FBQzNDLFFBQU0sRUFBRTtBQUNOLE1BQUUsRUFBRSxPQUFPO0FBQ1gsWUFBUSxFQUFFLEtBQUs7QUFDZixjQUFVLEVBQUUsaUJBQWlCO0dBQzlCO0FBQ0QsT0FBSyxFQUFFLGlCQUFXO0FBQ2hCLGFBQVMsQ0FBQyxNQUFNLEVBQUUsQ0FBQztHQUNwQjtBQUNELEtBQUc7Ozs7Ozs7Ozs7S0FBRSxVQUFTLEdBQUcsRUFBQztBQUNoQixXQUFPLENBQUMsTUFBTSxDQUFDLEVBQUMsSUFBSSxFQUFFLEdBQUcsRUFBQyxDQUFDLENBQUM7R0FDN0IsQ0FBQTtBQUNELGlCQUFlLEVBQUUseUJBQVMsSUFBSSxFQUFDO0FBQzdCLHNCQUFrQixDQUFDLE1BQU0sQ0FBQyxFQUFDLEVBQUUsRUFBRSxJQUFJLEVBQUMsQ0FBQyxDQUFDO0dBQ3ZDO0NBQ0YsQ0FBQyxDQUFDO1FBZlUsTUFBTSxHQUFOLE1BQU0iLCJmaWxlIjoiZ2VuZXJhdGVkLmpzIiwic291cmNlUm9vdCI6IiIsInNvdXJjZXNDb250ZW50IjpbIihmdW5jdGlvbiBlKHQsbixyKXtmdW5jdGlvbiBzKG8sdSl7aWYoIW5bb10pe2lmKCF0W29dKXt2YXIgYT10eXBlb2YgcmVxdWlyZT09XCJmdW5jdGlvblwiJiZyZXF1aXJlO2lmKCF1JiZhKXJldHVybiBhKG8sITApO2lmKGkpcmV0dXJuIGkobywhMCk7dmFyIGY9bmV3IEVycm9yKFwiQ2Fubm90IGZpbmQgbW9kdWxlICdcIitvK1wiJ1wiKTt0aHJvdyBmLmNvZGU9XCJNT0RVTEVfTk9UX0ZPVU5EXCIsZn12YXIgbD1uW29dPXtleHBvcnRzOnt9fTt0W29dWzBdLmNhbGwobC5leHBvcnRzLGZ1bmN0aW9uKGUpe3ZhciBuPXRbb11bMV1bZV07cmV0dXJuIHMobj9uOmUpfSxsLGwuZXhwb3J0cyxlLHQsbixyKX1yZXR1cm4gbltvXS5leHBvcnRzfXZhciBpPXR5cGVvZiByZXF1aXJlPT1cImZ1bmN0aW9uXCImJnJlcXVpcmU7Zm9yKHZhciBvPTA7bzxyLmxlbmd0aDtvKyspcyhyW29dKTtyZXR1cm4gc30pIiwiXG5pbXBvcnQge1JvdXRlcn0gZnJvbSAnLi9yb3V0ZXInO1xuXG5cbiQoZnVuY3Rpb24oKXtcbiAgbGV0IGFwcFJvdXRlciA9IG5ldyBSb3V0ZXIoKTtcbiAgQmFja2JvbmUuaGlzdG9yeS5zdGFydCh7cHVzaFN0YXRlOiB0cnVlLCByb290OiBcIi9hZG1pbi9cIn0pO1xuICB3aW5kb3cuZXZlbnRCdXMgPSBfLmNsb25lKEJhY2tib25lLkV2ZW50cyk7XG4gIHdpbmRvdy5ldmVudEJ1cy5vbignbmF2aWdhdGUnLCBmdW5jdGlvbihtc2cpe1xuICAgIGFwcFJvdXRlci5uYXZpZ2F0ZShtc2csIHt0cmlnZ2VyOiB0cnVlfSk7XG4gIH0pXG59KTtcblxuIiwiXG5leHBvcnQgY29uc3QgSW5kZXhNb2RlbCA9IEJhY2tib25lLk1vZGVsLmV4dGVuZCh7XG4gIHVybCA6IGZ1bmN0aW9uKCl7XG4gICAgcmV0dXJuICcvYWRtaW4vZGFzaGJvYXJkJztcbiAgfVxufSk7XG4iLCJcbmV4cG9ydCBjb25zdCBJdGVtQ29sbGVjdGlvbk1vZGVsID0gQmFja2JvbmUuTW9kZWwuZXh0ZW5kKHtcbiAgdXJsIDogZnVuY3Rpb24oaWQpe1xuICAgIHJldHVybiAnL2FkbWluL2ljLycgKyB0aGlzLmdldCgnaWQnKTtcbiAgfVxufSk7XG4iLCJcbmV4cG9ydCBjb25zdCBPcmdNb2RlbCA9IEJhY2tib25lLk1vZGVsLmV4dGVuZCh7XG4gIHVybCA6IGZ1bmN0aW9uKG5hbWUpe1xuICAgIGNvbnNvbGUubG9nKHRoaXMuZ2V0KCduYW1lJykpO1xuICAgIHJldHVybiAnL2FkbWluL28vJyArIHRoaXMuZ2V0KCduYW1lJyk7XG4gIH1cbn0pO1xuIiwiZXhwb3J0IGNvbnN0IEluZGV4VGVtcGxhdGUgPSBgXG4gIHt7I29yZ3N9fVxuICAgIDxhIGhyZWY9XCJqYXZhc2NyaXB0OnZvaWQoMClcIiBvbi1jbGljaz1cIm5hdmlnYXRlXCI+e3t0aXRsZX19PC9hPlxuICB7ey99fVxuYFxuIiwiZXhwb3J0IGNvbnN0IFRhYmxlVGVtcGxhdGUgPSBgXG4gIDxkaXYgY2xhc3M9XCJ0YWJsZS1yZXNwb25zaXZlIHN0YXRzXCI+XG4gICAgPHRhYmxlIGNsYXNzPVwidGFibGUgdGFibGUtYm9yZGVyZWQgdGFibGUtaG92ZXIgc3RhdHMtdGFibGVcIj5cbiAgICAgIDx0aGVhZD5cbiAgICAgICAgPHRyIGNsYXNzPVwiaW5mb1wiPlxuICAgICAgICAgIDx0aD4jPC90aD5cbiAgICAgICAgICA8dGg+SXRlbTwvdGg+XG4gICAgICAgICAgPHRoPkF2YWlsYWJsZTwvdGg+XG4gICAgICAgICAgPHRoPlNvbGQ8L3RoPlxuICAgICAgICAgIDx0aD5GcmVlPC90aD5cbiAgICAgICAgICA8dGg+Q2FuY2VsbGVkPC90aD5cbiAgICAgICAgPC90cj5cbiAgICAgIDwvdGhlYWQ+XG4gICAgICA8dGJvZHk+XG4gICAgICAgIHt7I2l0ZW1zfX1cbiAgICAgICAgICA8dHI+XG4gICAgICAgICAgICA8dGQ+e3sgQGluZGV4ICsgMSB9fTwvdGQ+XG4gICAgICAgICAgICA8dGQ+e3sgdGl0bGUgfX08L3RkPlxuICAgICAgICAgICAgPHRkPnt7IGF2YWlsYWJsZSB9fTwvdGQ+XG4gICAgICAgICAgICA8dGQ+e3sgc29sZCB9fTwvdGQ+XG4gICAgICAgICAgICA8dGQ+e3sgZnJlZSB9fTwvdGQ+XG4gICAgICAgICAgICA8dGQ+e3sgY2FuY2VsbGVkIH19PC90ZD5cbiAgICAgICAgICA8L3RyPlxuICAgICAgICB7ey99fVxuICAgICAgPC90Ym9keT5cbiAgICA8L3RhYmxlPlxuICA8L2Rpdj5cbmBcblxuZXhwb3J0IGNvbnN0IEl0ZW1Db2xsZWN0aW9uVGVtcGxhdGUgPSBgXG4gIDxUYWJsZUNvbXBvbmVudD48L1RhYmxlQ29tcG9uZW50PlxuYFxuIiwiZXhwb3J0IGNvbnN0IG9yZ1RlbXBsYXRlID0gYFxuICA8dWw+XG4gICAge3sjaXRlbV9jb2xsZWN0aW9uc319XG4gICAgICA8bGk+XG4gICAgICAgIDxhIGhyZWY9XCJqYXZhc2NyaXB0OnZvaWQoMClcIiBvbi1jbGljaz1cIm5hdmlnYXRlXCI+e3t0aXRsZX19PC9hPlxuICAgICAgPC9saT5cbiAgICB7ey99fVxuICA8L3VsPlxuYFxuIiwiXG5pbXBvcnQge0luZGV4TW9kZWx9IGZyb20gJy4uL21vZGVscy9pbmRleC5qcyc7XG5pbXBvcnQge0luZGV4VGVtcGxhdGV9IGZyb20gJy4uL3RlbXBsYXRlcy9pbmRleC5odG1sLmpzJztcblxuZXhwb3J0IGNvbnN0IEluZGV4VmlldyA9IHtcbiAgcmVuZGVyOiBmdW5jdGlvbigpIHtcbiAgICBjb25zb2xlLmxvZyghdGhpcy5yYWN0aXZlKTtcbiAgICBpZiAoIXRoaXMuaW5kZXhNb2RlbCkge1xuICAgICAgdGhpcy5pbmRleE1vZGVsID0gbmV3IEluZGV4TW9kZWwoKTtcbiAgICB9XG4gICAgdGhpcy5pbmRleE1vZGVsLmZldGNoKCkudGhlbihmdW5jdGlvbihkYXRhKXtcbiAgICAgIGlmICghdGhpcy5yYWN0aXZlKSB7XG4gICAgICAgIGNvbnNvbGUubG9nKFwicmFjdGl2ZVwiKVxuICAgICAgICB0aGlzLnJhY3RpdmUgPSBuZXcgUmFjdGl2ZSh7XG4gICAgICAgICAgZWw6ICcjbWFpbi1jb250ZW50LWFyZWEnLFxuICAgICAgICAgIHRlbXBsYXRlOiBJbmRleFRlbXBsYXRlLFxuICAgICAgICAgIGRhdGE6IHtcbiAgICAgICAgICAgIG9yZ3M6IGRhdGEub3Jnc1xuICAgICAgICAgIH1cbiAgICAgICAgfSk7XG4gICAgICAgIHRoaXMucmFjdGl2ZS5vbignbmF2aWdhdGUnLCBmdW5jdGlvbihldmVudCwgbWV0aG9kKXtcbiAgICAgICAgICAvLyBjb25zb2xlLmxvZyhldmVudC5jb250ZXh0LnVybCk7XG4gICAgICAgICAgZXZlbnRCdXMudHJpZ2dlcignbmF2aWdhdGUnLCBldmVudC5jb250ZXh0LnVybCk7XG4gICAgICAgIH0pO1xuICAgICAgfSBlbHNlIHtcbiAgICAgICAgdGhpcy5yYWN0aXZlLnJlbmRlcigpO1xuICAgICAgfVxuICAgIH0pXG4gIH1cbn1cbiIsIlxuaW1wb3J0IHtJdGVtQ29sbGVjdGlvbk1vZGVsfSBmcm9tICcuLi9tb2RlbHMvaXRlbV9jb2xsZWN0aW9uLmpzJztcbmltcG9ydCB7VGFibGVUZW1wbGF0ZSwgSXRlbUNvbGxlY3Rpb25UZW1wbGF0ZX0gZnJvbSAnLi4vdGVtcGxhdGVzL2l0ZW1fY29sbGVjdGlvbi5odG1sLmpzJztcblxuLy8gQ29tcG9uZW50c1xuLy8gdGFibGVcbi8vIGNoYXJ0XG5cbmxldCBUYWJsZUNvbXBvbmVudCA9IFJhY3RpdmUuZXh0ZW5kKHtcbiAgaXNvbGF0ZWQ6IGZhbHNlLFxuICB0ZW1wbGF0ZTogVGFibGVUZW1wbGF0ZVxufSk7XG5cbmV4cG9ydCBjb25zdCBJdGVtQ29sbGVjdGlvblZpZXcgPSB7XG4gIGluaXQ6IGZ1bmN0aW9uKGRhdGEpe1xuICAgIHRoaXMucmFjdGl2ZSA9IG5ldyBSYWN0aXZlKHtcbiAgICAgIGVsOiAnI21haW4tY29udGVudC1hcmVhJyxcbiAgICAgIHRlbXBsYXRlOiBJdGVtQ29sbGVjdGlvblRlbXBsYXRlLFxuICAgICAgZGF0YToge1xuICAgICAgICBpdGVtczogdGhpcy5tb2RlbC5nZXQoJ2l0ZW1zJylcbiAgICAgIH0sXG4gICAgICBjb21wb25lbnRzOiB7VGFibGVDb21wb25lbnQ6IFRhYmxlQ29tcG9uZW50fVxuICAgIH0pO1xuXG4gICAgdGhpcy5tb2RlbC5vbignY2hhbmdlOml0ZW1zJywgKG1vZGVsLCBpdGVtcykgPT4gdGhpcy5yYWN0aXZlLnNldCgnaXRlbXMnLCBpdGVtcykpO1xuXG4gICAgdGhpcy5yYWN0aXZlLm9uKCduYXZpZ2F0ZScsIGZ1bmN0aW9uKGV2ZW50LCBtZXRob2Qpe1xuICAgICAgLy8ga2lsbCBpbnRlcnZhbFxuICAgICAgY2xlYXJJbnRlcnZhbCh0aGlzLmludGVydmFsSWQpO1xuICAgICAgZXZlbnRCdXMudHJpZ2dlcignbmF2aWdhdGUnLCBldmVudC5jb250ZXh0LnVybCk7XG4gICAgfSk7XG4gICAgd2luZG93LmFkZEV2ZW50TGlzdGVuZXIoJ3BvcHN0YXRlJywgKGV2ZW50KSA9PiB7XG4gICAgICAvLyBraWxsIGludGVydmFsXG4gICAgICBjbGVhckludGVydmFsKHRoaXMuaW50ZXJ2YWxJZCk7XG4gICAgfSk7XG4gIH0sXG4gIHJlZnJlc2g6IGZ1bmN0aW9uKCl7XG4gICAgdGhpcy5tb2RlbC5mZXRjaCgpLnRoZW4oZGF0YSA9PiB0aGlzLm1vZGVsLnNldCgnaXRlbXMnLCBkYXRhLml0ZW1zKSk7XG4gIH0sXG4gIHJlbmRlcjogZnVuY3Rpb24oaW5pdERhdGEpIHtcbiAgICB0aGlzLm1vZGVsID0gbmV3IEl0ZW1Db2xsZWN0aW9uTW9kZWwoe1xuICAgICAgaWQ6IGluaXREYXRhLmlkXG4gICAgfSk7XG5cbiAgICB0aGlzLm1vZGVsLmZldGNoKCkudGhlbihkYXRhID0+IHtcbiAgICAgIHRoaXMubW9kZWwuc2V0KCdpdGVtcycsIGRhdGEuaXRlbXMpO1xuICAgICAgdGhpcy5pbml0KCk7XG4gICAgfSk7XG5cbiAgICB0aGlzLmludGVydmFsSWQgPSBzZXRJbnRlcnZhbCgoKSA9PiB0aGlzLnJlZnJlc2goKSwgMzAwMCk7XG4gIH1cbn1cbiIsIlxuaW1wb3J0IHtPcmdNb2RlbH0gZnJvbSAnLi4vbW9kZWxzL29yZy5qcyc7XG4vLyBpbXBvcnQge3JlbmRlcnZpZXd9IGZyb20gJy4vcmVuZGVydmlldy5qcyc7XG5pbXBvcnQge29yZ1RlbXBsYXRlfSBmcm9tICcuLi90ZW1wbGF0ZXMvb3JnLmh0bWwuanMnO1xuXG5leHBvcnQgY29uc3QgT3JnVmlldyA9IHtcbiAgcmVuZGVyOiBmdW5jdGlvbihvcmcpIHtcbiAgICBpZiAoIXRoaXMub3JnTW9kZWwpIHtcbiAgICAgIHRoaXMub3JnTW9kZWwgPSBuZXcgT3JnTW9kZWwoe1xuICAgICAgICBuYW1lOiBvcmcubmFtZVxuICAgICAgfSk7XG4gICAgfVxuICAgIHRoaXMub3JnTW9kZWwuZmV0Y2goKS50aGVuKGZ1bmN0aW9uKGRhdGEpe1xuICAgICAgaWYgKCF0aGlzLnJhY3RpdmUpIHtcbiAgICAgICAgdGhpcy5yYWN0aXZlID0gbmV3IFJhY3RpdmUoe1xuICAgICAgICAgIGVsOiAnI21haW4tY29udGVudC1hcmVhJyxcbiAgICAgICAgICAvLyB0ZW1wbGF0ZTogJyNvcmctY29udGVudC10ZW1wbGF0ZScsXG4gICAgICAgICAgdGVtcGxhdGU6IG9yZ1RlbXBsYXRlLFxuICAgICAgICAgIGRhdGE6IHtcbiAgICAgICAgICAgIG5hbWU6IGRhdGEubmFtZSxcbiAgICAgICAgICAgIGl0ZW1fY29sbGVjdGlvbnM6IGRhdGEuaXRlbV9jb2xsZWN0aW9uc1xuICAgICAgICAgIH1cbiAgICAgICAgfSk7XG4gICAgICAgIHRoaXMucmFjdGl2ZS5vbignbmF2aWdhdGUnLCBmdW5jdGlvbihldmVudCwgbWV0aG9kKXtcbiAgICAgICAgICAvLyBjb25zb2xlLmxvZyhldmVudC5jb250ZXh0LnVybCk7XG4gICAgICAgICAgZXZlbnRCdXMudHJpZ2dlcignbmF2aWdhdGUnLCBldmVudC5jb250ZXh0LnVybCk7XG4gICAgICAgIH0pO1xuXG4gICAgICB9IGVsc2Uge1xuICAgICAgICB0aGlzLnJhY3RpdmUucmVuZGVyKCk7XG4gICAgICB9XG4gICAgfSk7XG5cbiAgfVxufVxuIiwiXG5pbXBvcnQge0luZGV4Vmlld30gZnJvbSAnLi9pbmRleC5qcyc7XG5pbXBvcnQge09yZ1ZpZXd9IGZyb20gJy4vb3JnLmpzJztcbmltcG9ydCB7SXRlbUNvbGxlY3Rpb25WaWV3fSBmcm9tICcuL2l0ZW1fY29sbGVjdGlvbi5qcyc7XG5cbmV4cG9ydCBjb25zdCBSb3V0ZXIgPSBCYWNrYm9uZS5Sb3V0ZXIuZXh0ZW5kKHtcbiAgcm91dGVzOiB7XG4gICAgXCJcIjogXCJpbmRleFwiLFxuICAgIFwiby86b3JnXCI6IFwib3JnXCIsXG4gICAgXCJpYy86aWNJZFwiOiBcIml0ZW1fY29sbGVjdGlvblwiXG4gIH0sXG4gIGluZGV4OiBmdW5jdGlvbigpIHtcbiAgICBJbmRleFZpZXcucmVuZGVyKCk7XG4gIH0sXG4gIG9yZzogZnVuY3Rpb24ob3JnKXtcbiAgICBPcmdWaWV3LnJlbmRlcih7bmFtZTogb3JnfSk7XG4gIH0sXG4gIGl0ZW1fY29sbGVjdGlvbjogZnVuY3Rpb24oaWNJZCl7XG4gICAgSXRlbUNvbGxlY3Rpb25WaWV3LnJlbmRlcih7aWQ6IGljSWR9KTtcbiAgfVxufSk7XG4iXX0=
