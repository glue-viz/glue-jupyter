<template>
    <v-btn-toggle v-model="active_tool_id" class="transparent">
        <v-btn v-for="[id, data] of Object.entries(tools_data)" :key="id" icon variant="text" :value="id">
            <img :src="data.img" width="20"/>
            <v-tooltip activator="parent" location="bottom">{{ data.tooltip }}</v-tooltip>
            <v-menu v-if="data.subtools" activator="parent">
                <v-list>
                    <v-list-item v-for="subdata in data.subtools"
                        :prepend-icon="subdata.img"
                        :title="subdata.tool_tip"
                    >
                    </v-list-item>
                </v-list>
            </v-menu>
        </v-btn>
    </v-btn-toggle>
</template>
