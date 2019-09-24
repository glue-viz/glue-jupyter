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
      class="elevation-1"
    >
      <template v-slot:header="props">
        <thead>
          <tr>
            <th style="padding: 0 10px">#</th>
            <th style="padding: 0 1px" v-if="selection_enabled">
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
        <tr>
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
          <td v-for="header in headers" class="text-xs-right" :key="header.text">
            <v-slide-x-transition appear>
              <span class="text-truncate" style="display: inline-block">{{ props.item[header.value] }}</span>
            </v-slide-x-transition>
          </td>
        </tr>
      </template>
    </v-data-table>
  </v-slide-x-transition>
</template>