<template>
  <v-slide-x-transition appear>
    <v-data-table
      dense
      hide-default-header
      :headers="[...headers]"
      :items="items"
      :footer-props="{'items-per-page-options': [10,20,50,100]}"
      :options.sync="options"
      :items_per_page.sync="items_per_page"
      :server-items-length="total_length"
      :class="['elevation-1', 'glue-data-table', scrollable && 'glue-data-table--scrollable']"
      :style="scrollable && height != null && `height: ${height}`"
    >
      <template v-slot:header="props">
        <thead>
          <tr>
            <th :style="'padding: 0 10px; width: '+Math.max(1, Math.ceil(Math.log10(total_length)))*20+'px'">#</th>
            <th style="padding: 0 1px; width: 30px" v-if="selection_enabled">
              <v-btn icon color="primary" text small @click="apply_filter">
                <v-icon>filter_list</v-icon>
              </v-btn>
            </th>
            <th style="padding: 0 1px" v-for="(header, index) in headers_selections" :key="header.text">
              <v-icon style="padding: 0 1px" :key="index" :color="selection_colors[index]">brightness_1</v-icon>
            </th>
            <v-slide-x-transition :key="header.text" v-for="header in headers">
              <th >{{ header.text }}</th>
            </v-slide-x-transition>
          </tr>
        </thead>
      </template>
      <template v-slot:item="props">
        <tr @click="on_row_clicked(props.item.__row__)" :class="{'highlightedRow': props.item.__row__ === highlighted}">
          <td style="padding: 0 10px" class="text-xs-left">
            <i>{{ props.item.__row__ }}</i>
          </td>
          <td style="padding: 0 1px" class="text-xs-left" v-if="selection_enabled">
            <v-checkbox
              hide-details style="margin-top: 0; padding-top: 0"
              :input-value="checked.indexOf(props.item.__row__) != -1"
              :key="props.item.__row__"
              @change="(value) => select({checked: value, row: props.item.__row__})"
            />
          </td>
          <td style="padding: 0 1px" :key="header.text" v-for="(header, index) in headers_selections">
            <v-fade-transition leave-absolute>
              <v-icon
                v-if="props.item[header.value]"
                v-model="props.item[header.value]"
                :color="selection_colors[index]"
              >brightness_1</v-icon>
            </v-fade-transition>
          </td>
          <td v-for="header in headers" class="text-xs-right"
              :key="header.text"
              class="text-truncate text-no-wrap"
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


<style id="glue_table">
.highlightedRow {
    background-color: #E3F2FD;
}

.glue-data-table table {
  table-layout: fixed;
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