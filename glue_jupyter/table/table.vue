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
              <v-btn icon color="primary" text small @click="toggle_select_all">
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
          <td v-for="header in headers"
              :key="header.text"
              class="text-truncate text-no-wrap glue-editable-cell"
              :title="props.item[header.value]"
              @dblclick="header.editable && startEdit(props.item.__row__, header.value, props.item[header.value])"
          >
              <div v-if="isEditing(props.item.__row__, header.value)" class="cell-edit-container">
                <v-text-field
                  v-model="editValue"
                  class="cell-edit-input"
                  dense
                  hide-details
                  single-line
                  autofocus
                  @focus="onEditFocus"
                  @keyup.enter="commitEdit"
                  @keyup.escape="cancelEdit"
                  @click.stop
                ></v-text-field>
                <div class="cell-edit-icons">
                  <v-icon
                    small
                    class="cell-edit-confirm"
                    color="success"
                    @click.native.stop="commitEdit"
                    title="Confirm (Enter)"
                  >mdi-check</v-icon>
                  <v-icon
                    small
                    class="cell-edit-cancel"
                    color="error"
                    @click.native.stop="cancelEdit"
                    title="Cancel (Escape)"
                  >mdi-close</v-icon>
                </div>
              </div>
              <span v-else class="cell-content">
                {{ props.item[header.value] }}
                <v-icon
                  v-if="header.editable"
                  x-small
                  class="edit-icon"
                  @click.stop="startEdit(props.item.__row__, header.value, props.item[header.value])"
                >mdi-pencil</v-icon>
              </span>
          </td>
        </tr>
      </template>
    </v-data-table>
  </v-slide-x-transition>
</template>

<script>
module.exports = {
  data: function() {
    return {
      editingCell: null,  // { row: number, column: string }
      editValue: ''
    };
  },
  methods: {
    toggleSort(column) {
      this.sort_column(column);
    },
    startEdit(row, column, currentValue) {
      this.editingCell = { row: row, column: column };
      this.editValue = currentValue !== null && currentValue !== undefined ? String(currentValue) : '';
    },
    cancelEdit() {
      this.editingCell = null;
      this.editValue = '';
    },
    commitEdit() {
      if (this.editingCell) {
        this.cell_edited({
          row: this.editingCell.row,
          column: this.editingCell.column,
          value: this.editValue
        });
        this.editingCell = null;
        this.editValue = '';
      }
    },
    isEditing(row, column) {
      return this.editingCell !== null &&
             this.editingCell.row === row &&
             this.editingCell.column === column;
    },
    onEditFocus(event) {
      // Move cursor to start so text isn't truncated at the beginning
      this.$nextTick(() => {
        const input = event.target;
        if (input && input.setSelectionRange) {
          input.setSelectionRange(0, 0);
        }
      });
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

/* Editable cell styles */
.glue-editable-cell .cell-content {
  display: inline-flex;
  align-items: center;
}

.glue-editable-cell .edit-icon {
  opacity: 0;
  transition: opacity 0.2s;
  margin-left: 4px;
  cursor: pointer;
}

.glue-editable-cell:hover .edit-icon {
  opacity: 0.5;
}

.glue-editable-cell .edit-icon:hover {
  opacity: 1;
}

.cell-edit-container {
  display: inline-flex;
  align-items: center;
}

.cell-edit-icons {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  margin-left: 4px;
}

.cell-edit-input {
  margin: 0;
  padding: 0;
  flex: 1;
  font-size: inherit;
}

.cell-edit-input input {
  font-size: inherit;
}

.cell-edit-input .v-input__slot {
  min-height: unset !important;
}

.cell-edit-confirm,
.cell-edit-cancel {
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.cell-edit-confirm:hover,
.cell-edit-cancel:hover {
  opacity: 1;
}
</style>
