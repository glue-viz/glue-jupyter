<template>
    <div class="glue-table-viewer-state">
        <v-select
            label="Visible columns"
            :items="column_items"
            v-model="visible_columns"
            multiple
            hide-details
        >
            <template v-slot:selection="{ index }">
                <span v-if="index === 0">
                    {{ visible_columns.length === column_items.length ? 'All columns' : `${visible_columns.length} of ${column_items.length} columns` }}
                </span>
            </template>
        </v-select>
        <v-select
            v-if="unit_column_items.length > 0"
            label="Column units"
            :items="unit_column_items"
            v-model="selected_unit_column"
            clearable
            hide-details
        ></v-select>
        <v-select
            v-if="selected_unit_column"
            label="Unit"
            :items="unit_choices"
            v-model="selected_unit"
            hide-details
        ></v-select>
    </div>
</template>
