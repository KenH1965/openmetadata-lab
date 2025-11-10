import React from 'react';
import './DataProductsWidget.css';

const DataProductsWidget: React.FC = () => {
    const dataProducts = [
        { id: 1, name: 'Product A', description: 'Description of Product A', metrics: 'Metric A' },
        { id: 2, name: 'Product B', description: 'Description of Product B', metrics: 'Metric B' },
        { id: 3, name: 'Product C', description: 'Description of Product C', metrics: 'Metric C' },
    ];

    return (
        <div className="data-products-widget">
            <h2>Data Products</h2>
            <ul>
                {dataProducts.map(product => (
                    <li key={product.id}>
                        <h3>{product.name}</h3>
                        <p>{product.description}</p>
                        <span>{product.metrics}</span>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default DataProductsWidget;