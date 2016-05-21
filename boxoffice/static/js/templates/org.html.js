export const orgTemplate = `
  <ul>
    {{#item_collections}}
      <li>
        <a href="javascript:void(0)" on-click="navigate">{{title}}</a>
      </li>
    {{/}}
  </ul>
`
