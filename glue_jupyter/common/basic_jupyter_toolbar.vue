<template>
    <v-btn-toggle v-model="active_tool_id" class="transparent">
        <template v-for="[id, data] of Object.entries(tools_data)">
            <!-- Tool with a target-picker menu (e.g. the path slicer):
                 the icon button itself opens the menu. Picking an item
                 both activates the tool and sets the chosen target via
                 vue_select_menu_item. -->
            <v-menu offset-y v-if="data.menu_labels" :key="id">
                <template v-slot:activator="{ on: menu_on }">
                    <v-tooltip bottom>
                        <template v-slot:activator="{ on: tip_on }">
                            <v-btn icon
                                   :input-value="active_tool_id === id"
                                   v-on="{...menu_on, ...tip_on}">
                                <img :src="data.img" width="20"/>
                            </v-btn>
                        </template>
                        <span>{{ data.tooltip }}</span>
                    </v-tooltip>
                </template>
                <v-list dense>
                    <v-list-item v-for="(label, i) of data.menu_labels"
                                 :key="i"
                                 @click="select_menu_item({tool_id: id, index: i})">
                        <v-list-item-icon v-if="i === data.menu_active_index">
                            <v-icon small>mdi-check</v-icon>
                        </v-list-item-icon>
                        <v-list-item-icon v-else>
                            <span style="width: 24px;"></span>
                        </v-list-item-icon>
                        <v-list-item-title>{{ label }}</v-list-item-title>
                    </v-list-item>
                </v-list>
            </v-menu>
            <!-- Plain tool (no menu): unchanged. -->
            <v-tooltip v-else bottom :key="id">
                <template v-slot:activator="{ on }">
                    <v-btn v-on="on" icon :value="id">
                        <img :src="data.img" width="20"/>
                    </v-btn>
                </template>
                <span>{{ data.tooltip }}</span>
            </v-tooltip>
        </template>
    </v-btn-toggle>
</template>
