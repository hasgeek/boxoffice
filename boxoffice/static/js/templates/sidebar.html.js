export const SideBarTemplate = `
  {{^sidebarHide}}
    <button class="sidebar-toggle {{#sidebarMobileOn}}open{{/}}" type="button" on-click="toggle(event)">
      <i class="fa {{#sidebarMobileOn}}fa-angle-double-left{{else}}fa-angle-double-right{{/}}"></i>
    </button>
    <div class="admin-sidebar {{#sidebarMobileOn}}active{{/}}">
      <div class="admin-sidebar-content">
        {{#sideBar}}
          <a class="sidebar-title {{#if activeItem === view}} active {{/if}}" href="javascript:void(0)" on-click="navigate(event)"><i class="sidebar-title-icon fa fa-fw {{icon}}"></i>{{ title }}</a>
        {{/sideBar}}
      </div>
    </div>
  {{/}}
`
