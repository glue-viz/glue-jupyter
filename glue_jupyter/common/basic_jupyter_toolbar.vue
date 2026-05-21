<template>
    <v-btn-toggle v-model="active_tool_id" class="transparent">
        <template v-for="[id, data] of Object.entries(tools_data)">
            <!-- Tool with a dropdown menu attached (e.g. the path
                 slicer's target picker): a tooltipped icon button that
                 activates the tool, and a small chevron beside it that
                 opens the menu. -->
            <template v-if="data.menu_labels">
                <v-tooltip bottom :key="id + '-btn'">
                    <template v-slot:activator="{ on }">
                        <v-btn v-on="on" icon :value="id">
                            <img :src="data.img" width="20"/>
                        </v-btn>
                    </template>
                    <span>{{ data.tooltip }}</span>
                </v-tooltip>
                <v-menu offset-y :key="id + '-menu'">
                    <template v-slot:activator="{ on }">
                        <v-btn v-on="on" icon x-small style="margin-left: -8px;">
                            <v-icon small>mdi-menu-down</v-icon>
                        </v-btn>
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
            </template>
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
