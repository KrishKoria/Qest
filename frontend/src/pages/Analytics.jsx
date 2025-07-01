import React from "react";
import { Card } from "../components/ui";
import { ChartBarIcon } from "@heroicons/react/24/outline";

const Analytics = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
          <p className="mt-1 text-sm text-gray-600">
            View detailed analytics and reports
          </p>
        </div>
      </div>

      <Card className="p-12 text-center">
        <ChartBarIcon className="mx-auto h-16 w-16 text-gray-400" />
        <h3 className="mt-4 text-lg font-medium text-gray-900">Coming Soon</h3>
        <p className="mt-2 text-gray-600">
          Advanced analytics and reporting features will be available in the
          next update.
        </p>
      </Card>
    </div>
  );
};

export default Analytics;
