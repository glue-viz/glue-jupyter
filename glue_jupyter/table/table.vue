<template>
  <v-slide-x-transition appear>
    <v-data-table
      density="compact"
      hide-default-header
      :headers="[...headers]"
      :items="items"
      :footer-props="{'items-per-page-options': [10,20,50,100]}"
      :options="options"
      @update:options="setOptions"
      :items-per-page="items_per_page"
      @update:items-per-page="setItemsPerPage"
      :server-items-length="total_length"
      :class="['elevation-1', 'glue-data-table', scrollable && 'glue-data-table--scrollable']"
      :style="scrollable && height != null && `height: ${height}`"
    >
      <template v-slot:header="props">
        <thead>
          <tr>
            <th :style="'padding: 0 10px; width: '+Math.max(1, Math.ceil(Math.log10(total_length)))*20+'px'">#</th>
            <th style="padding: 0 1px; width: 30px" v-if="selection_enabled">
              <v-btn icon color="primary" variant="text" size="small" @click="apply_filter">
                <v-icon>{{ all_selected ? 'check_box' : (checked.length > 0 ? 'indeterminate_check_box' : 'check_box_outline_blank') }}</v-icon>
              </v-btn>
            </th>
            <th style="padding: 0 1px" v-for="(header, index) in headers_selections" :key="header.text">
              <v-icon style="padding: 0 1px" :key="index" :color="selection_colors[index]">brightness_1</v-icon>
            </th>
            <th v-for="header in headers"
                :key="header.text"
                @click="toggleSort(header.value)"
                style="cursor: pointer; user-select: none;"
            >
              {{ header.text }}
              <v-icon v-if="options.sortBy && options.sortBy[0] === header.value">
                {{ options.sortDesc && options.sortDesc[0] ? 'arrow_drop_down' : 'arrow_drop_up' }}
              </v-icon>
            </th>
          </tr>
        </thead>
      </template>
      <template v-slot:item="props">
        <tr @click="on_row_clicked(props.item.__row__)" :class="{'highlightedRow': props.item.__row__ === highlighted}">
          <td style="padding: 0 10px" class="text-left">
            <i>{{ props.item.__row__ }}</i>
          </td>
          <td style="padding: 0 1px" class="text-left" v-if="selection_enabled">
            <v-checkbox
              hide-details style="margin-top: 0; padding-top: 0"
              :model-value="checked.indexOf(props.item.__row__) != -1"
              :key="props.item.__row__"
              @update:modelValue="(value) => select({checked: value, row: props.item.__row__})"
            />
          </td>
          <td style="padding: 0 1px" :key="header.text" v-for="(header, index) in headers_selections">
            <v-fade-transition leave-absolute>
              <v-icon
                v-if="props.item[header.value]"
                :color="selection_colors[index]"
              >brightness_1</v-icon>
            </v-fade-transition>
          </td>
          <td v-for="header in headers"
              :key="header.text"
              class="text-right text-truncate text-no-wrap"
              :title="props.item[header.value]"
          >
            <v-slide-x-transition appear>
              <span>{{ props.item[header.value] }}</span>
            </v-slide-x-transition>
          </td>
        </tr>
      </template>
    </v-data-table>
  </v-slide-x-transition>
</template>

<script>
module.exports = {
  methods: {
    toggleSort(column) {
      this.sort_column(column);
    },
    setOptions(nextOptions) {
      const next = nextOptions || {};
      const page = Number(next.page);
      const itemsPerPage = Number(next.itemsPerPage);
      const normalized = {
        page: Number.isFinite(page) ? page : this.options.page,
        itemsPerPage: Number.isFinite(itemsPerPage) ? itemsPerPage : this.options.itemsPerPage,
        sortBy: Array.isArray(next.sortBy)
          ? next.sortBy.map((entry) => (typeof entry === 'object' && entry !== null ? entry.key : entry)).filter((v) => v != null)
          : [],
        sortDesc: Array.isArray(next.sortBy) && next.sortBy.length > 0 && typeof next.sortBy[0] === 'object'
          ? next.sortBy.map((entry) => entry && entry.order === 'desc')
          : (Array.isArray(next.sortDesc) ? next.sortDesc.slice() : []),
        totalItems: this.total_length,
      };
      if (JSON.stringify(normalized) !== JSON.stringify(this.options)) {
        this.options = normalized;
      }
    },
    setItemsPerPage(value) {
      const pageSize = Number(value);
      if (!Number.isFinite(pageSize) || this.items_per_page === pageSize) {
        return;
      }
      this.items_per_page = pageSize;
      this.options = {
        ...this.options,
        itemsPerPage: pageSize,
        totalItems: this.total_length,
      };
    }
  }
}
</script>

<style id="glue_table">
.highlightedRow {
    background-color: #E3F2FD;
}

.glue-data-table .v-data-table__wrapper {
  overflow-x: auto;
}

.glue-data-table table {
  table-layout: auto;
}

.glue-data-table th,
.glue-data-table td {
  white-space: nowrap;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.glue-data-table--scrollable .v-data-table__wrapper {
  overflow-y: auto;
  height: calc(100% - 59px);
}

.glue-data-table--scrollable thead > tr {
  position: sticky;
  top: 0;
}

.glue-data-table--scrollable .v-data-table__wrapper,
.glue-data-table--scrollable .v-data-table__wrapper > table,
.glue-data-table--scrollable .v-data-table__wrapper > table thead,
.glue-data-table--scrollable .v-data-table__wrapper > table thead *
{
  background-color: inherit;
}

/* prevent checkboxes overlaying the table header */
.glue-data-table--scrollable .v-data-table__wrapper > table thead {
  position: relative;
  z-index: 1;
}
</style>
