import React from "react";
import { Card } from "../components/ui";
import { QuestionMarkCircleIcon } from "@heroicons/react/24/outline";

const Support = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Support</h1>
          <p className="mt-1 text-sm text-gray-600">
            Get help and contact support
          </p>
        </div>
      </div>

      <Card className="p-12 text-center">
        <QuestionMarkCircleIcon className="mx-auto h-16 w-16 text-gray-400" />
        <h3 className="mt-4 text-lg font-medium text-gray-900">
          Support Center
        </h3>
        <p className="mt-2 text-gray-600">
          Support functionality and help documentation will be available in the
          next update.
        </p>
      </Card>
    </div>
  );
};

export default Support;
