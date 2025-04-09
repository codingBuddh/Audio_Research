import React from 'react';
import {
  VStack,
  Checkbox,
  CheckboxGroup,
  Button,
  Text,
  Box,
  Heading,
} from '@chakra-ui/react';
import { AudioFeatureType } from '../types';

const FEATURE_OPTIONS = [
  {
    type: AudioFeatureType.ACOUSTIC,
    label: "Acoustic Features",
  }
];

interface FeatureSelectorProps {
  selectedFeatures: AudioFeatureType[];
  onFeaturesChange: (features: AudioFeatureType[]) => void;
  isAnalyzing: boolean;
  onAnalyze: () => void;
}

export const FeatureSelector: React.FC<FeatureSelectorProps> = ({
  selectedFeatures,
  onFeaturesChange,
  isAnalyzing,
  onAnalyze,
}) => {
  return (
    <VStack spacing={6} align="stretch" w="100%" p={4}>
      <Box>
        <Heading size="md" mb={4}>Select Analysis Features</Heading>
        <VStack align="start" spacing={4}>
          {FEATURE_OPTIONS.map((feature) => (
            <Checkbox
              key={feature.type}
              value={feature.type}
              isChecked={selectedFeatures.includes(feature.type)}
              onChange={(e) => {
                const newFeatures = e.target.checked
                  ? [...selectedFeatures, feature.type]
                  : selectedFeatures.filter(f => f !== feature.type);
                onFeaturesChange(newFeatures);
              }}
              isDisabled={isAnalyzing}
              w="100%"
            >
              <Text fontWeight="medium">{feature.label}</Text>
            </Checkbox>
          ))}
        </VStack>
      </Box>
      
      <Button
        colorScheme="blue"
        isDisabled={selectedFeatures.length === 0 || isAnalyzing}
        isLoading={isAnalyzing}
        loadingText="Analyzing..."
        onClick={onAnalyze}
        size="lg"
      >
        Analyze Audio
      </Button>
    </VStack>
  );
}; 