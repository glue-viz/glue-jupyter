<template>
    <div>
        <v-toolbar dense class="elevation-0">
            <v-toolbar-items>
                <jupyter-widget :widget="controls.toolbar_selection_tools"></jupyter-widget>
                <jupyter-widget :widget="controls.toolbar_selection_mode"></jupyter-widget>
                <jupyter-widget :widget="controls.toolbar_active_subset"></jupyter-widget>
                <v-spacer></v-spacer>
                <v-app-bar-nav-icon @click="drawer_open = !drawer_open"></v-app-bar-nav-icon>
            </v-toolbar-items>
        </v-toolbar>
        <v-row no-gutters>
            <v-col cols="12">
                <jupyter-widget :widget="controls.figure_widget"></jupyter-widget>
            </v-col>
            <v-col cols="12">
                <jupyter-widget :widget="controls.output_widget"></jupyter-widget>
            </v-col>
        </v-row>
        <v-navigation-drawer v-model="drawer_open" absolute right width="min-content">
            <v-app-bar-nav-icon @click="drawer_open = !drawer_open"></v-app-bar-nav-icon>
            <v-expansion-panels v-model="open_panels" multiple accordion style="padding-left: 1px; min-width: 200px">
                <v-expansion-panel>
                    <v-expansion-panel-header class="font-weight-bold">Viewer Options</v-expansion-panel-header>
                    <v-expansion-panel-content>
                        <jupyter-widget :widget="controls.viewer_options"></jupyter-widget>
                    </v-expansion-panel-content>
                </v-expansion-panel>
                <v-expansion-panel>
                    <v-expansion-panel-header class="font-weight-bold">Layer Options</v-expansion-panel-header>
                    <v-expansion-panel-content>
                        <jupyter-widget :widget="controls.layer_options"></jupyter-widget>
                    </v-expansion-panel-content>
                </v-expansion-panel>
            </v-expansion-panels>
        </v-navigation-drawer>
    </div>
</template>
