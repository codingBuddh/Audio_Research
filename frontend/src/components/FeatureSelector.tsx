import {
  VStack,
  Heading,
  Button,
  Checkbox,
  CheckboxGroup,
} from '@chakra-ui/react'
import { AudioFeatureType } from '../types'

interface FeatureSelectorProps {
  selectedFeatures: AudioFeatureType[]
  onChange: (features: AudioFeatureType[]) => void
  onAnalyze: () => void
  isAnalyzing: boolean
}

const FEATURE_OPTIONS = [
  { value: AudioFeatureType.MFCC, label: 'Mel-frequency Cepstral Coefficients (MFCC)' },
  { value: AudioFeatureType.PITCH, label: 'Pitch Analysis' },
  { value: AudioFeatureType.EMOTION_SCORES, label: 'Emotion Analysis' },
  { value: AudioFeatureType.SPEAKING_RATE, label: 'Speaking Rate' },
]

export const FeatureSelector = ({
  selectedFeatures,
  onChange,
  onAnalyze,
  isAnalyzing,
}: FeatureSelectorProps) => {
  return (
    <VStack align="stretch" spacing={4}>
      <Heading size="md" mb={2}>
        Select Features
      </Heading>
      
      <CheckboxGroup
        value={selectedFeatures}
        onChange={(values) => onChange(values as AudioFeatureType[])}
      >
        <VStack align="start" spacing={3}>
          {FEATURE_OPTIONS.map((option) => (
            <Checkbox key={option.value} value={option.value}>
              {option.label}
            </Checkbox>
          ))}
        </VStack>
      </CheckboxGroup>

      <Button
        colorScheme="brand"
        size="lg"
        onClick={onAnalyze}
        isLoading={isAnalyzing}
        loadingText="Analyzing..."
        isDisabled={selectedFeatures.length === 0 || isAnalyzing}
        w="full"
        mt={4}
      >
        Analyze Audio
      </Button>
    </VStack>
  )
} 