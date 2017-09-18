export const SideBarTemplate = `
  {{^sidebarHide}}
    <button class="sidebar-toggle {{#sidebarMobileOn}}open{{/}}" type="button" on-click="toggle(event)">
      <i class="fa {{#sidebarMobileOn}}fa-close{{else}}fa-bars{{/}}"></i>
    </button>
    <div class="admin-sidebar {{#sidebarMobileOn}}active{{/}}">
      <div class="admin-sidebar-content">
        {{#sidebarItems}}
          {{#url}}
            <a class="sidebar-title {{#if activeItem === view}}active{{/if}} {{#subItem}}sidebar-subitem{{/}}" title="{{ title }}" href="javascript:void(0)" on-click="navigate(event)"><i class="sidebar-title-icon fa fa-fw {{icon}}"></i>{{ title }}</a>
          {{/}}
        {{/sidebarItems}}
      </div>
    </div>
  {{/}}
`
