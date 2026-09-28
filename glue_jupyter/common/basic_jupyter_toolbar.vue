<template>
    <v-btn-toggle v-model="active_tool_id" class="transparent">
        <v-tooltip v-for="[id, data] of Object.entries(tools_data)" location="bottom">
            <template v-slot:activator="{ props }">
                <v-menu v-if="data.subtools" v-bind="props">
                    <template v-slot:activator="{ props: menuProps }">
                        <v-btn v-bind="menuProps" icon variant="text" :value="id">
                            <img :src="data.img" width="20"/>
                        </v-btn>
                    </template>
                    <v-list>
                        <v-list-item v-for="subdata in data.subtools"
                            :prepend-icon="subdata.img"
                            :title="subdata.tool_tip"
                        >
                        </v-list-item>
                    </v-list>
                </v-menu>
                <v-btn v-else v-bind="props" icon variant="text" :value="id">
                    <img :src="data.img" width="20"/>
                </v-btn>
            </template>
            <span>{{ data.tooltip }}</span>
        </v-tooltip>
    </v-btn-toggle>
</template>
