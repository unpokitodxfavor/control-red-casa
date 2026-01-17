import React from 'react';
import NetworkMap from '../NetworkMap';

const NetworkMapWidget = ({ devices }) => {
    return (
        <div style={{ height: '100%', width: '100%', overflow: 'hidden' }}>
            <NetworkMap devices={devices} isWidget={true} />
        </div>
    );
};

export default NetworkMapWidget;
