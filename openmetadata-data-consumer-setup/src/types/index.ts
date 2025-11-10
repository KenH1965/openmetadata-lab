export interface DataConsumerRole {
    id: string;
    name: string;
    permissions: string[];
}

export interface DataConsumerPersona {
    id: string;
    displayName: string;
    preferences: {
        landingPage: string;
        theme: string;
    };
}

export interface DataProduct {
    id: string;
    name: string;
    description: string;
    metrics: {
        views: number;
        downloads: number;
    };
}

export interface WidgetConfig {
    id: string;
    title: string;
    dataSource: string;
    layout: {
        width: number;
        height: number;
    };
}