export const SideBarTemplate = `
  {{#sideBarView}}
  <button class="sidebar-toggle {{#sidebarOn}}open{{/}}" type="button" on-click="toggle(event)">
    <i class="fa {{#sidebarOn}}fa-angle-double-left{{else}}fa-angle-double-right{{/}}"></i>
  </button>
  <div class="ic-sidebar {{#sidebarOn}}active{{/}}">
    <div class="ic-sidebar-content">
      {{#sideBar}}
        <a class="sidebar-title" {{#url}}href="javascript:void(0)" on-click="navigate(event)"{{/}}><i class="sidebar-title-icon fa {{icon}}"></i>{{ title }}</a>
      {{/sideBar}}
    </div>
  </div>
  {{/}}
`