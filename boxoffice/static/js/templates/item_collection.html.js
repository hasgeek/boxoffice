export const TableTemplate = `
  <div class="table-responsive stats">
    <table class="table table-bordered table-hover stats-table">
      <thead>
        <tr class="info">
          <th>#</th>
          <th>Item</th>
          <th>Available</th>
          <th>Sold</th>
          <th>Free</th>
          <th>Cancelled</th>
        </tr>
      </thead>
      <tbody>
        {{#items}}
          <tr>
            <td>{{ @index + 1 }}</td>
            <td>{{ title }}</td>
            <td>{{ available }}</td>
            <td>{{ sold }}</td>
            <td>{{ free }}</td>
            <td>{{ cancelled }}</td>
          </tr>
        {{/}}
      </tbody>
    </table>
  </div>
`

export const ItemCollectionTemplate = `
  <TableComponent></TableComponent>
`
