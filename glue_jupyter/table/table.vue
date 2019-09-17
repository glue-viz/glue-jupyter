<template>
  <v-slide-x-transition appear>
    <v-data-table
      :headers="[...headers_selections, ...headers]"
      :items="items"
      :rows-per-page-items="[10,20,50,100]"
      :pagination.sync="pagination"
      :total-items="total_length"
      class="elevation-1"
    >
      <template v-slot:headers="props">
        <th style="padding: 0 10px">#</th>
        <th style="padding: 0 1px">
          <v-btn icon color="primary" flat small @click="apply_filter">
            <v-icon>filter_list</v-icon>
          </v-btn>
        </th>
        <th style="padding: 0 1px" v-for="(header, index) in headers_selections" :key="header.text">
          <v-icon style="padding: 0 1px" :key="index" :color="selection_colors[index]">brightness_1</v-icon>
        </th>
        <v-slide-x-transition :key="header.text" v-for="header in headers">
          <th >{{ header.text }}</th>
        </v-slide-x-transition>
      </template>
      <template v-slot:items="props">
        <td style="padding: 0 10px" class="text-xs-left">
          <i>{{ props.item.__row__ }}</i>
        </td>
        <td style="padding: 0 1px" class="text-xs-left">
          <v-checkbox
            hide-details
            :input-value="checked.indexOf(props.item.__row__) != -1"
            :key="props.item.__row__"
            @change="(value) => select({checked: value, row: props.item.__row__})"
          />
        </td>
        <td style="padding: 0 1px" :key="props.item[header.value]" v-for="(header, index) in headers_selections">
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
            <span>{{ props.item[header.value] }}</span>
          </v-slide-x-transition>
        </td>
      </template>
    </v-data-table>
  </v-slide-x-transition>
</template>