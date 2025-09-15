import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  Alert,
  CircularProgress,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import { DataGrid, GridActionsCellItem } from '@mui/x-data-grid';
import { Upload as UploadIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';

interface Document {
  id: number;
  filename: string;
  original_filename: string;
  file_type: string;
  file_size: number;
  upload_path: string;
  processing_status: string;
  created_at: string;
  uploaded_by: number;
}

const Documents: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [deleteDialog, setDeleteDialog] = useState<{ open: boolean; docId: number | null }>({
    open: false,
    docId: null,
  });
  const { isAdmin } = useAuth();

  useEffect(() => {
    if (isAdmin) {
      fetchDocuments();
    }
  }, [isAdmin]);

  const fetchDocuments = async () => {
    try {
      const response = await axios.get('/documents');
      setDocuments(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch documents');
    } finally {
      setLoading(false);
    }
  };

  const onDrop = async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    
    // Check for duplicate filename on frontend
    const existingDocument = documents.find(doc => doc.filename === file.name);
    if (existingDocument) {
      setError(`Document with filename "${file.name}" already exists. Please use a different filename or delete the existing document first.`);
      return;
    }

    setUploading(true);
    setError('');
    setSuccess('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      await axios.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setSuccess(`File "${file.name}" uploaded successfully!`);
      fetchDocuments(); // Refresh the list
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
    disabled: uploading,
  });

  const handleDeleteDocument = async () => {
    if (!deleteDialog.docId) return;

    try {
      await axios.delete(`/documents/${deleteDialog.docId}`);
      setSuccess('Document deleted successfully!');
      fetchDocuments(); // Refresh the list
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete document');
    } finally {
      setDeleteDialog({ open: false, docId: null });
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const columns = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'filename', headerName: 'Filename', width: 200 },
    { field: 'file_type', headerName: 'Type', width: 100 },
    { 
      field: 'file_size', 
      headerName: 'Size', 
      width: 100,
      renderCell: (params) => formatFileSize(params.value),
    },
    { 
      field: 'processing_status', 
      headerName: 'Status', 
      width: 120,
      renderCell: (params) => {
        const status = params.value;
        const getStatusColor = (status: string) => {
          switch (status) {
            case 'completed': return 'success';
            case 'processing': return 'warning';
            case 'failed': return 'error';
            case 'pending': return 'default';
            default: return 'default';
          }
        };
        
        const getStatusLabel = (status: string) => {
          switch (status) {
            case 'completed': return 'Completed';
            case 'processing': return 'Processing';
            case 'failed': return 'Failed';
            case 'pending': return 'Pending';
            default: return status;
          }
        };
        
        return (
          <Chip
            label={getStatusLabel(status)}
            color={getStatusColor(status)}
            size="small"
          />
        );
      },
    },
    { 
      field: 'created_at', 
      headerName: 'Uploaded', 
      width: 150,
      renderCell: (params) => new Date(params.value).toLocaleDateString(),
    },
    {
      field: 'actions',
      type: 'actions',
      headerName: 'Actions',
      width: 100,
      getActions: (params) => [
        <GridActionsCellItem
          icon={<DeleteIcon />}
          label="Delete"
          onClick={() => setDeleteDialog({ open: true, docId: params.id as number })}
          color="primary"
        />,
      ],
    },
  ];

  if (!isAdmin) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Alert severity="error">
          Admin access required to view documents.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom sx={{ color: '#0000fe', fontWeight: 'bold' }}>
        📄 Document Management
      </Typography>
      
      <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 4 }}>
        Upload and manage your documents
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      {/* Upload Area */}
      <Paper
        elevation={2}
        sx={{ p: 4, mb: 4, borderRadius: 3 }}
      >
        <Typography variant="h6" gutterBottom>
          📤 Upload Documents
        </Typography>
        
        <Box
          {...getRootProps()}
          sx={{
            border: '2px dashed',
            borderColor: isDragActive ? '#0000fe' : '#ccc',
            borderRadius: 3,
            p: 6,
            textAlign: 'center',
            cursor: 'pointer',
            backgroundColor: isDragActive ? '#f0f0ff' : '#fafafa',
            transition: 'all 0.3s ease',
            '&:hover': {
              borderColor: '#0000fe',
              backgroundColor: '#f0f0ff',
            },
          }}
        >
          <input {...getInputProps()} />
          {uploading ? (
            <Box>
              <CircularProgress sx={{ mb: 2 }} />
              <Typography>Uploading...</Typography>
            </Box>
          ) : (
            <Box>
              <UploadIcon sx={{ fontSize: 48, color: '#0000fe', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                {isDragActive ? 'Drop the file here' : 'Drag & drop a file here'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                or click to select a file
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Supported formats: PDF, DOCX, TXT
              </Typography>
            </Box>
          )}
        </Box>
        
        {/* Show existing documents to help avoid duplicates */}
        {documents.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              📋 Existing documents:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {documents.slice(0, 5).map((doc) => (
                <Chip
                  key={doc.id}
                  label={doc.filename}
                  size="small"
                  variant="outlined"
                  sx={{ fontSize: '0.7rem' }}
                />
              ))}
              {documents.length > 5 && (
                <Chip
                  label={`+${documents.length - 5} more`}
                  size="small"
                  variant="outlined"
                  sx={{ fontSize: '0.7rem' }}
                />
              )}
            </Box>
          </Box>
        )}
      </Paper>

      {/* Documents Table */}
      <Paper elevation={2} sx={{ borderRadius: 3 }}>
        <Box sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            📋 Uploaded Documents ({documents.length})
          </Typography>
        </Box>
        
        <Box sx={{ height: 500, width: '100%', px: 2, pb: 2 }}>
          {loading ? (
            <LoadingSpinner message="Loading documents..." />
          ) : (
            <DataGrid
              rows={documents}
              columns={columns}
              pageSizeOptions={[5, 10, 25]}
              initialState={{
                pagination: {
                  paginationModel: { page: 0, pageSize: 10 },
                },
              }}
              disableRowSelectionOnClick
              sx={{
                border: 'none',
                '& .MuiDataGrid-cell': {
                  borderBottom: '1px solid #f0f0f0',
                },
              }}
            />
          )}
        </Box>
      </Paper>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialog.open}
        onClose={() => setDeleteDialog({ open: false, docId: null })}
      >
        <DialogTitle>Delete Document</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this document? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog({ open: false, docId: null })}>
            Cancel
          </Button>
          <Button onClick={handleDeleteDocument} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Documents;

