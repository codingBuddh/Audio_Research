import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Box, Text, Icon, VStack } from '@chakra-ui/react'
import { FiUploadCloud } from 'react-icons/fi'

interface FileUploaderProps {
  onFileSelect: (file: File) => void
}

export const FileUploader = ({ onFileSelect }: FileUploaderProps) => {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onFileSelect(acceptedFiles[0])
      }
    },
    [onFileSelect]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.mp3', '.wav', '.m4a', '.aac', '.ogg']
    },
    maxFiles: 1,
  })

  return (
    <Box
      {...getRootProps()}
      p={10}
      border="2px dashed"
      borderColor={isDragActive ? 'brand.500' : 'gray.200'}
      borderRadius="lg"
      bg={isDragActive ? 'brand.50' : 'transparent'}
      cursor="pointer"
      transition="all 0.2s"
      _hover={{
        borderColor: 'brand.500',
        bg: 'brand.50',
      }}
    >
      <input {...getInputProps()} />
      <VStack spacing={2}>
        <Icon as={FiUploadCloud} w={10} h={10} color="gray.400" />
        <Text color="gray.600" textAlign="center">
          {isDragActive
            ? 'Drop the audio file here'
            : 'Drag and drop an audio file here, or click to select'}
        </Text>
        <Text fontSize="sm" color="gray.500">
          Supports MP3, WAV, M4A, AAC, and OGG
        </Text>
      </VStack>
    </Box>
  )
} 