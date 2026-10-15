import 'package:flutter/material.dart';
import '../models/doctor.dart';
import '../models/pg.dart';
import '../services/pg_service.dart';
import '../services/doctor_service.dart';
import '../services/auth_service.dart';

class SelectDutyPGScreen extends StatefulWidget {
  final Doctor doctor;

  const SelectDutyPGScreen({super.key, required this.doctor});

  @override
  State<SelectDutyPGScreen> createState() => _SelectDutyPGScreenState();
}

class _SelectDutyPGScreenState extends State<SelectDutyPGScreen> {
  // Define primary color
  static const _primaryColor = Color(0xFF3A418E);

  List<PG> _pgs = [];
  bool _loading = true;
  String? _error;
  PG? _selectedPG;
  bool _settingDuty = false;

  @override
  void initState() {
    super.initState();
    _loadPGs();
  }

  Future<void> _loadPGs() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      // Fetch PGs created by this doctor
      final result = await PGService.listPGs(
        createdBy: widget.doctor.id,
        limit: 100,
      );

      if (mounted) {
        setState(() {
          _loading = false;
          if (result['success'] == true) {
            _pgs = result['pgs'] as List<PG>;
          } else {
            _error = result['error'] ?? 'Failed to load PGs';
          }
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _loading = false;
          _error = 'Error loading PGs: $e';
        });
      }
    }
  }

  Future<void> _confirmDuty() async {
    final currentUser = AuthService.currentUser;
    if (currentUser == null) return;

    setState(() {
      _settingDuty = true;
    });

    try {
      // 1. Set Doctor on Duty
      final docResult = await DoctorService.setDutyDoctor(
        adminId: currentUser.id,
        doctorId: widget.doctor.id,
      );

      if (docResult['success'] != true) {
        throw Exception(docResult['error'] ?? 'Failed to set doctor on duty');
      }

      // 2. Set PG on Duty (if selected)
      if (_selectedPG != null) {
        final pgResult = await PGService.setDutyPG(
          doctorId: widget.doctor.id, // Using doctor ID as per API req
          pgId: _selectedPG!.id,
        );
        if (pgResult['success'] != true) {
          // Non-fatal, but warn
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                  content:
                      Text('Doctor set, but PG failed: ${pgResult['error']}')),
            );
          }
        }
      }

      if (mounted) {
        Navigator.pop(context, true); // Return success
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _settingDuty = false;
        });
      }
    }
  }

  Future<void> _showCreatePGDialog() async {
    final nameController = TextEditingController();
    final emailController = TextEditingController();
    final passwordController = TextEditingController();

    final result = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Create New PG'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameController,
                maxLength: 100,
                decoration: const InputDecoration(
                  labelText: 'Name *',
                  hintText: 'Enter full name (2-100 characters)',
                  border: OutlineInputBorder(),
                  counterText: '',
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: emailController,
                maxLength: 120,
                decoration: const InputDecoration(
                  labelText: 'Email *',
                  hintText: 'example@domain.com',
                  border: OutlineInputBorder(),
                  counterText: '',
                ),
                keyboardType: TextInputType.emailAddress,
              ),
              const SizedBox(height: 12),
              TextField(
                controller: passwordController,
                maxLength: 128,
                decoration: const InputDecoration(
                  labelText: 'Password *',
                  hintText: 'Min 8 chars: letters, numbers, symbols',
                  border: OutlineInputBorder(),
                  counterText: '',
                ),
                obscureText: true,
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: _primaryColor),
            onPressed: () {
              final name = nameController.text.trim();
              final email = emailController.text.trim();
              final password = passwordController.text;

              // Basic validation (same as Doctor Dashboard)
              if (name.length < 2) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Name too short')),
                );
                return;
              }
              if (email.isEmpty || !email.contains('@')) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Invalid email')),
                );
                return;
              }
              if (password.length < 8) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Password too short (min 8)')),
                );
                return;
              }

              Navigator.pop(ctx, true);
            },
            child: const Text('Create', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );

    if (result != true) return;

    // Create PG
    final createResult = await PGService.createPG(
        name: nameController.text.trim(),
        email: emailController.text.trim(),
        password: passwordController.text,
        doctorId: widget.doctor.id // Create for THIS doctor
        );

    if (mounted) {
      if (createResult['success'] == true) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('PG created successfully')),
        );
        _loadPGs(); // Refresh list
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(createResult['error'] ?? 'Failed to create PG'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Select Duty PG'),
        backgroundColor: _primaryColor,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            onPressed: _showCreatePGDialog,
            icon: const Icon(Icons.person_add),
            tooltip: 'Create PG',
          ),
        ],
      ),
      body: Column(
        children: [
          // Header info
          Container(
            padding: const EdgeInsets.all(20),
            color: _primaryColor.withOpacity(0.05),
            width: double.infinity,
            child: Column(
              children: [
                Text(
                  'Setting Duty Doctor',
                  style: TextStyle(
                    color: _primaryColor,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  widget.doctor.name,
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Select a PG to assist this doctor (optional)',
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ],
            ),
          ),

          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator())
                : _error != null
                    ? Center(
                        child: Text(_error!,
                            style: const TextStyle(color: Colors.red)))
                    : _pgs.isEmpty
                        ? Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                const Icon(Icons.person_off,
                                    size: 48, color: Colors.grey),
                                const SizedBox(height: 16),
                                Text(
                                  'No PGs found for ${widget.doctor.name}',
                                  style: const TextStyle(
                                      fontSize: 16, color: Colors.grey),
                                ),
                              ],
                            ),
                          )
                        : ListView.builder(
                            padding: const EdgeInsets.all(16),
                            itemCount: _pgs.length,
                            itemBuilder: (context, index) {
                              final pg = _pgs[index];
                              final isSelected = _selectedPG?.id == pg.id;

                              return Card(
                                elevation: isSelected ? 4 : 1,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12),
                                  side: isSelected
                                      ? const BorderSide(
                                          color: _primaryColor, width: 2)
                                      : BorderSide.none,
                                ),
                                child: RadioListTile<PG>(
                                  value: pg,
                                  groupValue: _selectedPG,
                                  activeColor: _primaryColor,
                                  onChanged: (val) {
                                    setState(() => _selectedPG = val);
                                  },
                                  title: Text(pg.name,
                                      style: const TextStyle(
                                          fontWeight: FontWeight.w600)),
                                  subtitle: Text(pg.email),
                                  secondary: CircleAvatar(
                                    backgroundColor: isSelected
                                        ? _primaryColor
                                        : _primaryColor.withOpacity(0.1),
                                    child: Text(
                                      pg.name.isNotEmpty ? pg.name[0] : 'P',
                                      style: TextStyle(
                                        color: isSelected
                                            ? Colors.white
                                            : _primaryColor,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                  controlAffinity:
                                      ListTileControlAffinity.trailing,
                                ),
                              );
                            },
                          ),
          ),

          // Bottom Action Bar
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 10,
                  offset: const Offset(0, -5),
                ),
              ],
            ),
            child: SafeArea(
              child: SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _settingDuty ? null : _confirmDuty,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _primaryColor,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: _settingDuty
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(
                              color: Colors.white, strokeWidth: 2),
                        )
                      : Text(
                          _selectedPG != null
                              ? 'Set Duty: ${widget.doctor.name} & ${_selectedPG!.name}'
                              : 'Set Duty: ${widget.doctor.name} Only',
                          style: const TextStyle(
                              fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
